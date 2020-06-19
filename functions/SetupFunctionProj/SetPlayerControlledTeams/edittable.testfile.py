if isinstance(teams, list):
        # get the table details
        table_config = json.load(open('local.settings.json'))['Values']['AzureWebJobsStorage']
        accountname = get_account_name(table_config)
        accountkey = get_account_key(table_config)
        print("accountname: " + accountname)
        print("accountkey: " + accountkey)
        # connect to the table and update the player controlled teams
        
        table_service = TableService(account_name=accountname, account_key=accountkey)
        query_string = "Name eq '"
        counter = 1
        for team in teams:
            if counter == len(teams):
                query_string += team + "'"
            else:
                query_string += team + "' or Name eq '"
            counter += 1

        print("query_string: " + query_string)
        returned_teams = table_service.query_entities('Teams', filter=query_string)
        
        for team in returned_teams:
            team.Controlled = "p1"
            table_service.update_entity('Teams', team)

        return func.HttpResponse("updated", status_code=200)