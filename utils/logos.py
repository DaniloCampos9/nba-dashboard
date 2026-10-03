from nba_api.stats.static import teams

def obter_url_logo_time(identifier):
    """Retorna a URL oficial do logo da NBA baseado no ID numérico ou na sigla (ex: LAL)."""
    all_teams = teams.get_teams()
    team_obj = None
    
    if identifier is None:
        return None
        
    if str(identifier).isdigit():
        team_obj = next((t for t in all_teams if t['id'] == int(identifier)), None)
    else:
        identifier_str = str(identifier).upper()
        team_obj = next((t for t in all_teams if t['abbreviation'] == identifier_str), None)
        
    if team_obj:
        team_id = team_obj['id']
        return f"https://cdn.nba.com/logos/nba/{team_id}/global/L/logo.svg"
    return None