#!/usr/bin/env python3

import glob
import sys
import pandas as pd

import sqlite_utils
import json

from geojson_to_sqlite import utils
import pdb


import click

@click.group()
def cli():
    pass

class CarrierLUT:
    def __init__(self, meta_dir=None):
        if not meta_dir:
            meta_dir="interesting-planes"
        carrier_dir=meta_dir+"/carrier"
        self.carrier_data={}
        for f in glob.glob(f"{carrier_dir}/*.csv"):
            name=f.split('/')[-1].split('.')[0]
            #print(f"Reading {name}")
            self.carrier_data[name]=pd.read_csv(f)

    def enrich_with_carrier_info(self, df):
        """Use this LUT to add several "IsX" columns to a DataFrame, where X is Cargo, Military, etc"""
        df["IsMilitary"] = df.index.str.startswith("AE", na=False)
        df["IsN"] = df.Flight.str.startswith("N",na=False)
        for name, dftmp in self.carrier_data.items():
            df[f"Is{name.capitalize()}"] = df.Flight.str.startswith(tuple(dftmp.CarrierCode), na=False)
        return df

    def get_categories(self):
        return ["IsMilitary", "IsN"] + [ f"Is{x.capitalize()}" for x in self.carrier_data.keys() ]


class RegionLUT:
    def __init__(self, meta_dir=None):
        if not meta_dir:
            meta_dir="interesting-planes"
        region_dir=meta_dir+"/regions"
        all_dfs=[]
        for f in glob.glob(f"{region_dir}/*.csv"):
            all_dfs.append(pd.read_csv(f))
        self.df_region = pd.concat(all_dfs)

    def enrich_points_with_regions(self, dfp):
        for i in range(len(self.df_region)):
            (name,LonMin,LonMax,LatMin,LatMax)=self.df_region.iloc[i][['Region','LonMin','LonMax','LatMin','LatMax']]
            name=f"Is{name}" #no need to re-capitalize
            dfp[name] = (dfp.Lon.astype(float) >= LonMin) & (dfp.Lon.astype(float) < LonMax) & \
                        (dfp.Lat.astype(float) >= LatMin) & (dfp.Lat.astype(float) < LatMax)
        return dfp
        

    def get_regions(self):
        return [ f"Is{x}" for x in self.df_region.Region.tolist() ]


class DayParser:
    def __init__(self, meta_dir, filename):

        # All data is stuffed in one csv
        self.df=pd.read_csv(filename,sep='\t', header=None)

        self.carrier_lut = CarrierLUT(meta_dir)
        self.region_lut = RegionLUT(meta_dir)
        
        self.dfm = self._extract_meta(self.df)
        self.dfp = self._extract_positions(self.df)
        self.dft = self._extract_track(self.dfm, self.dfp)

        #print(self.dft)

    def _extract_meta(self, df):
        # Split out the plane metadata
        dfm=df[df[0]==1]
        dfm = (dfm
              .rename(columns={1:"ICAO",2:"Flight"})[['ICAO','Flight']]
              .groupby(by='ICAO')
              .first()
              .reset_index()
          )
        dfm.index = dfm.pop("ICAO")
        dfm["Flight"]=dfm.Flight.str.rstrip()
        return dfm

    def _extract_positions(self, df):
        # Extract the positions
        dfp=df[df[0]==3].copy()
        
        # Make the date and drop unused
        dfp["Date"] = pd.to_datetime(dfp[5] + " " + dfp[6])
        dfp = dfp.rename(columns={1:"ICAO",2:"Lat",3:"Lon",4:"Alt"})[["ICAO","Date","Lat","Lon","Alt"]]

        # Many planes don't report altitude. Zero out and convert to int
        dfp["Alt"] = dfp.Alt.fillna(0).astype(int)
        
        # Get rid of any rows where lat/lon are missing
        # NOTE There are a lot of planes (500?) that report altitude, but not pos
        dfp = dfp.dropna(subset=['Lat','Lon'])
        
        # Make a LonLat string so we can join whole string later
        dfp["LonLat"] = "[ " + dfp.Lon + ", " + dfp.Lat +" ]" 
        
        # Check each point to see if it's in any of the desired regions
        dfp = self.region_lut.enrich_points_with_regions(dfp)        
        
        # Sort by date here to be safe. Do icao first though to make planes easier to debug
        dfp = dfp.sort_values(by=["ICAO","Date"],ascending=True)
        return dfp

    def _extract_track(self, dfm, dfp):
        # Assemble all the points into tracks
        # Step 1: Organize by track and pick out the custom things
        dft1 = (dfp.groupby(by="ICAO")
                .agg( 
                    NumPoints=('LonLat','count'),
                    AltMin=('Alt','min'),
                    AltMax=('Alt','max'),
                    DateStart=('Date','first'), 
                    DateStop=('Date','last'), 
                    Coords=('LonLat',list),
                    Alts=('Alt',list))
               )

        # Step 2: Pull out all IsX columns and set True if a plane had any true values
        cmd={}
        for c in dfp.columns:
            if c.startswith("Is"):
                cmd[c]="any"
        dft2 = dfp.groupby(by="ICAO").agg(cmd) 

        # Merge into one table
        dft = dft1.join(dft2)
        
        # Convert coords to a string
        dft["Coords"] = dft['Coords'].str.join(',')
        
        # Add in the flight names
        dft = dft.join(dfm)
    
        # Insert any carrier info we have
        dft=self.carrier_lut.enrich_with_carrier_info(dft)
        
        # Reorder columns
        #dft = dft[["Flight","NumPoints", "IsLivermore", "IsMilitary", "IsPassenger", "IsExecutive", "IsMedical", "IsCargo", "IsOrganization","IsN","DateStart", "DateStop", "Coords", "Alts"]]
        
        dft = dft.reset_index() #Move icao back into list
        return dft
        
    def _geojson_single(self, i):


        all_is_columns= [ c for c in self.dft.columns if c.startswith("Is") ]
        is_columns=[]
        for c in all_is_columns:
            is_columns.append(f'   "{c}":"{int(self.dft.iloc[i][c])}"')

        is_section=",\n".join(is_columns)
       
        
        return f"""
{{
  "type":"Feature",
   "properties": {{
      "GEO_ID":"{self.dft.iloc[i].ICAO}",
      "Flight":"{self.dft.iloc[i].Flight}",
      "NumPoints":"{self.dft.iloc[i].NumPoints}",
      {is_section}
      }},
   "geometry": {{
      "type": "LineString",
      "coordinates": [ 
         {self.dft.iloc[i].Coords}
      ]
   }}
}}
"""      

    def to_geojson(self, file):

        if not file:
            f=sys.stdout
        else:
            print(f"File is {file}")
            f=open(file,'w')
        
        all_planes=[]
        for i in range(len(self.dft)):
            all_planes.append(self._geojson_single(i))
            
        print(f"""
{{
  "type": "FeatureCollection",
  "features":[
  {",".join(all_planes)}
  ]
}}
""", file=f)
        f.close()

             

@cli.command()
@click.option('--meta-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False, help='Path to interesting-planes root directory.')
def dump_carriers(meta_dir):
    """Read metadata abd list carrier categories"""
    carrier_lut = CarrierLUT(meta_dir)
    print(f"Categories: {', '.join(carrier_lut.get_categories())}")


@cli.command()
@click.option('--meta-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False, help='Path to interesting-planes root directory.')
def dump_regions(meta_dir):
    """Read metadata and list geo regions"""
    region_lut = RegionLUT(meta_dir)
    print(f"Regions: {', '.join(region_lut.get_regions())}")


@cli.command()
@click.option('--meta-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False, help='Path to interesting-planes root directory.')
@click.argument('source-csv',required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--dest-json', type=click.Path(exists=False, file_okay=True, dir_okay=False), required=False, help='Optional output file')
def convert_day(meta_dir, source_csv, dest_json):
    """Parse a single day and save the result"""
    day_parser = DayParser(meta_dir, source_csv)
    day_parser.to_geojson(dest_json)


@cli.command()
@click.option('--meta-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False, help='Path to interesting-planes root directory.')
@click.argument('source-csv',required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False))
def gen_db(meta_dir, source_csv):
    """WORK-IN-PROGRESS Non functional"""
    """Parse a single day and save the result"""

    file="/tmp/flights.geojson"
    table="tracks"
    db_path="/tmp/flights.db"
    nl=False
    pk=None
    alter=False
    properties={}
    spatialite=False
    spatial_index=False
    spatialite_mod=None
    
    day_parser = DayParser(meta_dir, source_csv)
    day_parser.to_geojson(file)

    try:
        features = utils.get_features(file, nl)
        utils.import_features(
            db_path,
            table,
            features,
            pk=pk,
            alter=alter,
            properties=properties,
            spatialite=spatialite,
            spatialite_mod=spatialite_mod,
            spatial_index=spatial_index,
        )
    except (TypeError, ValueError) as e:
        print(str(e))


if __name__ == '__main__':
    cli()
