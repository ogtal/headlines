import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from headlines_helper import create_name_dict
from orm import State, Base

database = 'test.db'

engine = create_engine(str('sqlite:///'+ database))
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

state_dict = create_name_dict(State, session)
#read states form csv
states_df = pd.read_csv('states.csv', names = ['state', 'state_description'])

for i,row in states_df.iterrows():
    state_name = row.state
    state_dscr = row.state_description
    #check if state is all ready in the database
    try:
        state = state_dict[state_name]
        #update description
        state.stata_decsription = state_dscr
        #commit change to database
        session.commit()
    except KeyError:  #KeyError is thrown if a state does not exist
        #create new state
        state = State(name = state_name, state_description = state_dscr)
        #add state to state dict
        state_dict[state_name] = state
        #add state to session and commit to, database
        session.add(state)
        session.commit()
#close session
session.close()