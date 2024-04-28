from dash import Dash, html, dcc, callback, Output, Input,dash_table, State
import plotly.express as px
import pandas as pd
import connections as con
import dash_bootstrap_components as dbc


c = con.connections()

external_stylesheets = [dbc.themes.CYBORG]
app = Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = dbc.Container([
	dbc.Row([
		html.Div(children = 'Keyword Data Overview', style = {'textAlign': 'center', 'fontSize': 35}),
		html.Div(className='row', children=[
			html.I("Enter Keyword: "),
			dcc.Input(id = "keyword_search", type ="search",value = 'complexity classes' ,placeholder= "keyword search"),  #text search
			])
		], className="h-15"),

	dbc.Row([
		dbc.Row([
				dbc.Col([
					dcc.Input(id = "fav_keyword", type ="text", placeholder= "Add / Delete keyword")
					], width = 5),
				dbc.Col([
					dcc.RadioItems(id = "Add_delete_fav",options = ['Add Keyword', 'Delete Keyword'], value = 'Add Keyword', inline=True)
					], width = 4),
				dbc.Col([	html.Button(id='submit_button', n_clicks=0, children='Submit')
					], width = 2),
						# ,
					# dash_table.DataTable( page_size = 5, id = 'search_history2') #search_history
			]),
		dbc.Row([
			html.Div(children = "Saved Favorites",style = {'textAlign': 'center', 'fontSize': 20}),
			dash_table.DataTable( page_size = 5, id = 'favorites',style_header={'color': 'black','fontWeight': 'bold','textAlign': 'left'},style_data={'color': 'black','textAlign': 'left'}) #favorites
			])
		]),
	dbc.Row([
		dbc.Col([
			html.Div(className='row', children=[
				html.Div(children = "Search History",style = {'textAlign': 'center', 'fontSize': 20}),
				dash_table.DataTable( page_size = 5, id = 'search_history',style_header={'color': 'black','fontWeight': 'bold','textAlign': 'left'},style_data={'color': 'black','textAlign': 'left'},style_table={'overflowX': 'auto'}) #search_history
				]),
			], width = 3),
		dbc.Col([
			html.Div(children = "Trend over years",style = {'textAlign': 'center', 'fontSize': 35}),
				dcc.Graph(figure ={}, id = 'publications_keyword_trend') #keyword_by_year_mgo
			], width = 8)
		]),
	dbc.Row([
		dbc.Col([
			html.Div(children = "Top Relevant Faculty",style = {'textAlign': 'center', 'fontSize': 35}),
			dash_table.DataTable( page_size = 5, id = 'relevant_faculty', style_table={'overflowX': 'auto'},style_header={'color': 'black','fontWeight': 'bold','textAlign': 'left'},style_data={'color': 'black','textAlign': 'left'}) #relevant_faculty_neo4j
			], width=6),
		dbc.Col([
			html.Div(className='row', children=[
				html.Div(children = "Top Relevant Universities",style = {'textAlign': 'center', 'fontSize': 35}),
				dash_table.DataTable( page_size = 5, id = 'relevant_uni', style_table={'overflowX': 'auto'},style_header={'color': 'black','fontWeight': 'bold','textAlign': 'left'},style_data={'color': 'black','textAlign': 'left'}) #relevant_uni_neo4j
				])
			], width=6)
		]),
	dbc.Row([
		html.Div(className='row', children=[
			html.Div(children = "Top Relevant Publications",style = {'textAlign': 'center', 'fontSize': 35}),
			dash_table.DataTable( page_size = 5, id = 'relevant_publications', style_table={'overflowX': 'auto'},style_header={'color': 'black','fontWeight': 'bold','textAlign': 'left'},style_data={'color': 'black','textAlign': 'left'}) #relevant_publications_neo4j
			])
		])

	], fluid=True,  style={"height": "100vh"})


#for search history data table
@callback(
	Output(component_id = 'search_history', component_property = 'data'),
	Input(component_id = 'keyword_search', component_property = 'value')
	)
def update_table(value):
	df = c.add_searched_word_mySQL(value)
	df = df.rename(columns = {0:'Keyword'})
	fig = df.to_dict('records')
	return fig

#add/ delete to favorite 
@callback(
	Output(component_id = 'favorites', component_property = 'data'),
	Input(component_id = 'submit_button', component_property = 'n_clicks'),
	State(component_id = 'fav_keyword', component_property ='value'),
	State(component_id ='Add_delete_fav', component_property ='value')
	)
def update_favorite(n_clicks,keyword,add_delete):

	if n_clicks>0 and add_delete == "Add Keyword" and keyword != None:
		c.add_favorite_word_mySQL(keyword)
	elif n_clicks> 0 and keyword != None:
		c.delete_favorite_word_mySQL(keyword)
	df = c.get_fav_keywords()
	df = df.rename(columns = {0:'Keyword',1:"Top Faculty Member",2:"Top University",3:"Top Journal"})
	fig = df.to_dict('records')
	# print('c')
	return fig


#publication keyword trend
@callback(
	Output(component_id = 'publications_keyword_trend', component_property = 'figure'),
	Input(component_id = 'keyword_search', component_property = 'value')
	)
def update_pub_key_trend(value):
	df = c.keyword_by_year_mgo(value)
	fig = px.line(df, x='_id', y='count', labels={"_id":"year",'count':'Number of publications'})
	return fig

#for facutly data table
@callback(
	Output(component_id = 'relevant_faculty', component_property = 'data'),
	Input(component_id = 'keyword_search', component_property = 'value')
	)
def update_table(value):
	df = c.relevant_faculty_neo4j(value)
	df = df.rename(columns = {0:'Faculty Name',1:'Affiliated University',2:'Keyword Score'})
	fig = df.to_dict('records')
	return fig

#for university data table
@callback(
	Output(component_id = 'relevant_uni', component_property = 'data'),
	Input(component_id = 'keyword_search', component_property = 'value')
	)
def update_table(value):
	df = c.relevant_uni_mySQL(value)
	# print(df)
	df = df.rename(columns = {0:'University',1:'Journal',2:'Paper Keyword Score'})
	fig = df.to_dict('records')
	return fig


#for facutly data table
@callback(
	Output(component_id = 'relevant_publications', component_property = 'data'),
	Input(component_id = 'keyword_search', component_property = 'value')
	)
def update_table(value):
	df = c.relevant_publications_neo4j(value)
	df = df.rename(columns = {0:'Name',1:'Journal', 2:'Keyword Score'})
	fig = df.to_dict('records')
	return fig

if __name__ == '__main__':
	app.run(debug=True)

