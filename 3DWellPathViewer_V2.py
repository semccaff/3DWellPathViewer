# %%
import geopandas as gpd
import numpy as np
from pandas import Series, DataFrame

import pandas as pd
from calendar import monthrange

import glob
import re
import time
import datetime as dt

import six
idx = pd.IndexSlice


import plotly.graph_objects as go
from plotly.subplots import make_subplots
import fiona
pd.set_option('display.max_columns', None)


# %%
df_WellPaths = gpd.read_file(r"D:\Documents - Data Drive\QGIS\GIS\Well_Locations\WellPaths\Township_66-126\ST37_WG_NAD83_10TM_AEP_TWP_66_126.shp")


# %%
well_list = pd.read_csv(r'D:\Documents - Data Drive\QGIS\Test\test.csv',header=None)
well_list.rename(columns={0:'Well_LicNo',1:'Wellname'},inplace=True)
well_list.drop_duplicates(inplace=True)
well_list['Well_LicNo'] = well_list['Well_LicNo'].apply('{:0>7}'.format)

lic_list = well_list["Well_LicNo"].tolist()

well_list.set_index('Well_LicNo',inplace=True)




# %%
df_data = df_WellPaths.set_index(['Well_LicNo']).loc[lic_list]
df_data = df_data[df_data.WGGeomSrce == 'Surveyed']
df_data = df_data.drop_duplicates().merge(well_list,on='Well_LicNo',how='left')


pattern =  r'(?<= )(\w|\w\w)\d.*?(?= )' #CNRL Jackfish and MEG CL Pattern
for index, row in df_data.iterrows(): 

    s_name = re.search(pattern,row["Wellname"]).group(0)
    df_data.at[index,'ShortName'] = s_name


df_data.ShortName = df_data.ShortName +" "+df_data.UWI_Label.str[-2:]


highlight = ['CNRL F12P LEISMER 8-5-76-6','CNRL F10P LEISMER 5-4-76-6','CNRL F11P LEISMER 4-4-76-6']
highlight_wells = df_data[df_data['Wellname'].isin(highlight)]['UWI_Label'].values


df_data = df_data.reset_index()
df_data = df_data.groupby(['Well_LicNo','UWI']).first().reset_index()
df_data.set_index('Well_LicNo',inplace=True)


import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots()
text_list = []

for i, UWI_Label in enumerate(df_data.UWI_Label):
    
    if UWI_Label in highlight_wells:
        line_color = dict(color="red")
        line_width = dict(width = 4)
    else:
        line_color = dict(color="black")
        line_width = dict(width= 2)

    
    df_plot = pd.DataFrame(list(df_data.geometry.iloc[i].coords))
    df_plot.columns = ['Long','Lat','TVD']
    df_plot['ShortName'] = df_data.ShortName.iloc[i]

    fig.add_trace(go.Scatter3d(
                    x=df_plot.Long, 
                    y=df_plot.Lat,
                    z=df_plot.TVD,
                    mode='lines',
                    marker= line_color,
                    line= line_width,
                    name = df_data.ShortName.iloc[i]))


    text_list = text_list + list(zip(df_plot.Long[-1:], df_plot[-1:].Lat, df_plot.TVD[-1:],df_plot.ShortName[-1:]))
    
#https://plotly.com/python/3d-axes/
ann = [dict(x=x, y=y, z=z, text=an_text,showarrow=False,xanchor="left",xshift=10,opacity=0.4) for x, y, z, an_text in text_list]

layout = go.Layout(
                title= dict(text = '<b>CNQ Jackfish Pad D Subsurface Wellpath Plot</b><br><sub><i>left click to rotate, right click to pan, scrollwheel to zoom</i></sub>',
                            font = dict(color = 'black',
                                        size = 30,
                                        family = 'Arial'),
                            y = 0.9,
                            x=0.5), 
                legend=dict(orientation="v",y=0.5),

                height=900,
                width=1500,
                margin=dict(r=10, b=10, l=10, t=10),
                scene=dict(xaxis_title='',
                            yaxis_title='',
                            zaxis_title='mASL',
                            
                            xaxis=dict(backgroundcolor="#FFFFFF",
                                gridcolor="white",
                                showbackground=True,
                                zerolinecolor="white",
                                ticktext= [''],
                                tickvals= [0]
                                ),
                            yaxis=dict(backgroundcolor="#FFFFFF",
                                gridcolor="white",
                                showbackground=True,
                                zerolinecolor="white",                                
                                ticktext= [''],
                                tickvals= [0]
                                ),
                            zaxis=dict(backgroundcolor="#F8F8F8",
                                gridcolor="#E8E8E8",
                                showbackground=True,
                                zerolinecolor="white",
                                color="black",
                                range=[150,230]),
                            annotations=ann

                        )
)

fig.update_layout(
                    scene_aspectmode='data',
                    legend_title_text='<b>Well Name / Event</b>',
                    legend_title_font_color='Black',
                    scene_camera=
                        dict(
                            eye=dict(x=-0.1, y=-1.75, z=0.02),
                            center=dict(x=-0.2, y=0.0, z=0),
                            )
                    )



fig.update_layout(layout)
fig.show()


fig.write_html('CNQ_cellar_wells3D.html')

# %%



