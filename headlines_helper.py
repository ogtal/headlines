#function for creating dictionary based on the name of entries in a sqlalchemy table. returns a dictionary.
#note that this function is not type safe at all.
def create_name_dict(table, session):
    #fetch all entris from table
    table_entries = session.query(table).all()
    table_dict = {}
    #loop trough  table entries and add to dict
    for entry in table_entries:
        table_dict[entry.name] = entry
    return table_dict

#function for creating dictionary based on the url of entries in a sqlalchemy table. returns a dictionary.
#note that this function is not type safe at all.
def create_url_dict(table, session):
    #fetch all entris from table
    table_entries = session.query(table).all()
    table_dict = {}
    #loop trough  table entries and add to dict
    for entry in table_entries:
        table_dict[entry.url] = entry
    return table_dict