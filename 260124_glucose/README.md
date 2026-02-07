# Glucose Monitor Plotter

This code is for plotting data I captured from a Lingo Glucose Monitor. It
should chop the data into 24-hour days and then plot it using green for
ok and red for out of band.

This code was generated through interactions with Cursor. See the other md
file for the transcript of the session.

I use uv to manage the python venv that the plotters need. The code should
be ok with any stock pandas python environment, but you can do
"uv sync" to create a venv with all the dependencies. 
