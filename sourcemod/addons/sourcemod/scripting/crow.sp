#include <sdktools>
#include <sourcemod>
#include <cstrike>
#include <ripext>
#define RED_TEAM 1
#define BLUE_TEAM 2
#define ChatAlias(%1,%2) \
if (StrEqual(sArgs[0], %1, false)) { \
    %2 (client, 0); \
}
HTTPClient httpClient;
char url[255];
char g_serverid[256];
char g_seckey[256];
char g_api_addr[256];
char g_red_team_steamid[6][64];
char g_blue_team_steamid[6][64];
//char g_player_unconnect[11][256];
//CT as 2,T as 1
int g_pause = 0;
int g_red_team = CS_TEAM_T;
int g_blue_team = CS_TEAM_CT;
int g_playerteam[MAXPLAYERS+1] = {0, ... };
int g_auth[MAXPLAYERS+1] = {false, ... };
int g_kill[MAXPLAYERS+1]= {0, ... };
int g_dead[MAXPLAYERS+1]= {0, ... };
int g_headshot[MAXPLAYERS+1]= {0, ... };
int g_helpshot[MAXPLAYERS+1]= {0, ... };
int g_firstshot[MAXPLAYERS+1]= {0, ... };

int g_red_team_score = 0;
int g_blue_team_score = 0;
int g_iRoundNumber = 0;
int g_PlayerNumber = 0;
bool g_change_team = false;
bool g_match = false;
bool first_bool = false;
bool g_match_finish = false;
bool g_red_team_pause = false;
bool g_blue_team_pause = false;
bool g_FreezeTime = false;
Handle BanTimers[MAXPLAYERS+1];

public Plugin:myinfo = 
{
	name = "CrowAntiCheat",
	author = "huoji",
	description = "huoji.ha4k1r",
	version = "1.0",
	url = "http://www.wghostk.com/"
}

public OnPluginStart()
{
	if(UpConfig()){
		PrintToServer("[Crow]Config was updated!");
	}else{
		PrintToServer("[Crow]Error! Config Not updated!");
		return;
	}
	HookEventEx("player_death",	Event_Player_Death);
	HookEventEx("player_connect_full", OnPlayerActivated); 
	HookEventEx("round_start", Event_Round_Start); 
	HookEventEx("round_end", Event_Round_End);
	HookEventEx("round_freeze_end", Event_Round_Freeze_End);
	RegConsoleCmd("status", block);
    RegConsoleCmd("ping", block);
	//HookConVarChange(FindConVar("mp_restartgame"), Event_Round_Restart);
	AddCommandListener(OnJoinTeam, "jointeam");
	ServerCommand("mp_autoteambalance 0");
	ServerCommand("mp_limitteams 0");
	ServerCommand("bot_quota 10");
	ServerCommand("bot_quota_mode Fill");
	ServerCommand("pvs_min_player_Distance 1");
	PrintToServer("Crow Anti Cheat Was Start!");
}

void InitPlugins(){
	g_red_team = 1;
	g_blue_team = 2;
	g_match = false;
	g_match_finish = false;
	g_red_team_score = 0;
	g_blue_team_score = 0;
	g_iRoundNumber = 0;
	g_PlayerNumber = 0;
	g_change_team = false;
	g_pause = 0;
	g_red_team_pause = false;
	g_blue_team_pause = false;
	ServerCommand("mp_autoteambalance 0");
	ServerCommand("mp_limitteams 0");
	ServerCommand("mp_unpause_match");
}
public Action OnBanClient(int client, int time, int flags, const char[] reason, const char[] kick_message, const char[] command, any source)
{
	PrintToChatAll("[反作弊] %N 因为使用作弊软件而被封禁!",client);
	//说明smac有检测了
	char steamid[64];
	if (GetClientAuthId(client, AuthId_SteamID64, steamid, sizeof(steamid))){
		Format(url, sizeof(url), "match_api/?request=smac_ban&key=%s&serverid=%s&steamid=%s", g_seckey,g_serverid,steamid);
		httpClient.Get(url, OnJsonRequest);
	}
	return Plugin_Continue;
}
public void OnClientPutInServer(int client)
{
	if(!g_match){	
		g_match = true;
		Format(url, sizeof(url), "match_api/?request=start_match&key=%s&serverid=%s", g_seckey,g_serverid);
		httpClient.Get(url, OnJsonRequest);	
	}
	return;
}
public Action OnClientSayCommand(int client, const char[]command, const char[]sArgs)
{
	ChatAlias("!pause", Pause)
	ChatAlias("!unpause", Unpause)
	return Plugin_Continue;
}
public Action Event_Round_Freeze_End(Handle event, const char[]name, bool dontBroadcast)
{
	g_FreezeTime = false;
	return Plugin_Continue;
}
public Action Event_Player_Death(Handle:event, const String:name[], bool:dontBroadcast)
{
	if(g_iRoundNumber <= 1)
		return;
	new victim = GetClientOfUserId(GetEventInt(event,"userid"));
	new attacker = GetClientOfUserId(GetEventInt(event, "attacker"));
	new assist = GetClientOfUserId(GetEventInt(event, "assister"));
	if(IsValidClient(victim) || IsValidClient(attacker))
		return;
	//自杀
	if(victim == attacker || attacker == 0)
		return;
	g_kill[attacker]++;
	g_dead[victim]++;
	new bool:headshot = GetEventBool(event, "headshot");
	if(headshot)
		g_headshot[attacker]++;
	if(first_bool){
		first_bool = false;
		g_firstshot[attacker]++;
	}
	if(!IsValidClient(assist)){
		g_helpshot[assist]++;
	}
}
public Action Event_Round_Start(Handle event, const char[]name, bool dontBroadcast)
{
	g_FreezeTime = true;
	g_iRoundNumber++;
	if(g_iRoundNumber >= 2)
		first_bool = true;
	return Plugin_Continue;
}


public Action Event_Round_End(Handle event, const char[]name, bool dontBroadcast)
{
	first_bool = false;
	int winner = GetEventInt(event, "winner");
	if(g_iRoundNumber == 0)
	{
		//热身也算一局
		if(g_PlayerNumber < 10){
			ServerCommand("mp_pause_match");
			PrintToChatAll("未满十人!服务器即将自动关闭!");
			PrintToChatAll("未满十人!服务器即将自动关闭!");
			PrintToChatAll("未满十人!服务器即将自动关闭!");
			Format(url, sizeof(url), "match_api/?request=post_finish&status=0&key=%s&serverid=%s", g_seckey,g_serverid);
			httpClient.Get(url, OnJsonRequest);
			DataPack pack;
			CreateDataTimer(5.0, kick_all_player, pack);
			pack.WriteString("未满十人!服务器即将自动关闭!");
		}
		return Plugin_Continue;
	}
	if (winner == g_blue_team)
		g_blue_team_score++;
	if (winner == g_red_team)
		g_red_team_score++;
	if(g_iRoundNumber > 1){
		Format(url, sizeof(url), "match_api/?request=push_score&key=%s&serverid=%s&red=%d&blue=%d", g_seckey,g_serverid,g_red_team_score,g_blue_team_score);
		httpClient.Get(url, OnJsonRequest);
	}
	if(g_iRoundNumber > 15 && !g_change_team){
		if(g_blue_team_score != 0 && g_red_team_score != 0)
		{
			g_blue_team = CS_TEAM_T;
			g_red_team = CS_TEAM_CT;
			g_change_team = true;
		}
	}
	if(g_red_team_score >= 16 || g_blue_team_score >= 16 || (g_blue_team_score == 15 && g_red_team_score == 15)){
		CreateTimer(0.1, push_data);
		g_match_finish = true;
		finish_match();
	}

	return Plugin_Continue;
}


public Action: OnPlayerActivated(Handle: pEvent, const String: pName[], bool: bNoBroadCast) 
{ 
	new client = GetClientOfUserId(GetEventInt(pEvent, "userid")); 
	if(IsValidClient(client))
		return Plugin_Continue;

	char steamid[64];
	int team_num = 0;
	if (GetClientAuthId(client, AuthId_SteamID64, steamid, sizeof(steamid))){
		if(CheckInRedTeam(steamid)){
			//PrintToServer("######## Red Team ########");
			g_playerteam[client] = RED_TEAM;
			team_num = g_red_team;
		}else if(CheckInBlueTeam(steamid)){
			//PrintToServer("######## BLue Team ########");
			g_playerteam[client] = BLUE_TEAM;
			team_num = g_blue_team;
		}else{
			g_auth[client] = false;
			KickClient(client,"You are not allowed to be on this server");
			return Plugin_Continue;
		}
		g_auth[client] = true;
		g_PlayerNumber++;
		Format(url, sizeof(url), "match_api/?request=add_connect&steamid=%s&key=%s&serverid=%s&client=%d", steamid,g_seckey,g_serverid,client);
		httpClient.Get(url, OnJsonRequest);
	}
    CS_SwitchTeam(client,team_num);
	SetEntProp(client, Prop_Send, "m_iTeamNum", team_num);
	SetEntPropFloat(client, Prop_Send, "m_fForceTeam", 0.0); 
	if(g_PlayerNumber == 10){
		ServerCommand("bot_kick");
	}
	return Plugin_Continue;
}

public Action: OnJoinTeam(client, const String: pCommand[], Args) 
{  
	if(IsValidClient(client))
		return Plugin_Continue;
    static String: Team[8]; 
    GetCmdArgString(Team, sizeof(Team)); 

    new SelectedTeam = StringToInt(Team); 
    if (SelectedTeam == CS_TEAM_SPECTATOR) 
        return Plugin_Stop; 
	
    return Plugin_Stop; 
}  
public void OnClientDisconnect(int client)
{	
	if(!g_match_finish){
		if(g_auth[client])
		{
			g_PlayerNumber = g_PlayerNumber -1;
			g_auth[client] = false;
			char steamid[64];
			if (GetClientAuthId(client, AuthId_SteamID64, steamid, sizeof(steamid))){
				Format(url, sizeof(url), "match_api/?request=del_connect&steamid=%s&key=%s&serverid=%s&client=%d", steamid,g_seckey,g_serverid,client);
				httpClient.Get(url, OnJsonRequest);
				float time = 180.0;
				if (g_pause != 0)
					time = 300.0;
				DataPack pack;	
				BanTimers[client] = CreateDataTimer(time, BanPlayer,pack);
				pack.WriteString(steamid);
				g_kill[client] = 0;
				g_headshot[client] = 0;
				g_helpshot[client] = 0;
				g_dead[client] = 0;
				g_firstshot[client] = 0;
			}
		}
	}

		
}
public void OnJsonRequest(HTTPResponse response, any value)
{
    if (response.Data == null) {
        PrintToServer("[CROW] ######response.Data was null######");
		//g_match = false;
        return;
    }
	char msgType[256];
	char steamid[64];
	int success;
	//int team;
	//int client;
    JSONObject json_request = view_as<JSONObject>(response.Data);
    json_request.GetString("msgType",msgType,sizeof(msgType));
	json_request.GetString("steamid",steamid,sizeof(steamid));
	success = json_request.GetInt("success");
	//team = json_request.GetInt("team");
	//client = json_request.GetInt("index");
	if(StrEqual(msgType,"start_match")){
		if(success == 0)
		{
			g_match = false;
			return;
		}	
		g_match = true;
		//InitPlugins();
		CreateTimer(30.0, timer_process, _, TIMER_REPEAT);
		char map[256];
		json_request.GetString("map",map,sizeof(map));
		char current_map[256];
		GetCurrentMap(current_map, 256)
		if (!StrEqual(current_map, map))
			ServerCommand("map %s", map);
		/*
		char json_players[256];
		json_request.GetString("players",json_players,sizeof(json_players));
		JSONArray PlayerArray = view_as<JSONArray>(json_request.Get("players"));  
		int num_player = PlayerArray.Length;
		for (int i = 0; i < num_player; i++) {
			char name[255];
			PlayerArray.GetString(i,name,sizeof(name));
			g_player_unconnect[i] = name;
			//PrintToServer(g_player_unconnect[i]);
		}*/
		JSONArray steam_id_array_red = view_as<JSONArray>(json_request.Get("red_team_steamid"));  
		int num_steamid = steam_id_array_red.Length;
		char m_steamid[64];
		for (int i = 0; i < num_steamid; i++) {	
			steam_id_array_red.GetString(i,m_steamid,sizeof(m_steamid));
			g_red_team_steamid[i] = m_steamid;
		//	PrintToServer(g_red_team_steamid[i]);
		}
		JSONArray steam_id_array_blue = view_as<JSONArray>(json_request.Get("blue_team_steamid"));  
		num_steamid = steam_id_array_blue.Length;
		for (int i = 0; i < num_steamid; i++) {
			steam_id_array_blue.GetString(i,m_steamid,sizeof(m_steamid));
			g_blue_team_steamid[i] = m_steamid;
		//	PrintToServer(g_blue_team_steamid[i]);
		}
		delete steam_id_array_red;
		delete steam_id_array_blue;
	}
	
	delete json_request;
}  
public Action push_data(Handle timer)
{
	char steamid[64];
	for(int i = 1; i <= MaxClients; i++)
	{
		if (IsValidClient(i)) continue;
		if (GetClientAuthId(i, AuthId_SteamID64, steamid, sizeof(steamid))){
			Format(url, sizeof(url), "match_api/?request=push_data&key=%s&serverid=%s&kill=%d&dead=%d&help=%d&firstshot=%d&headshot=%d&steamid=%s", g_seckey,g_serverid,g_kill[i],g_dead[i],g_helpshot[i],g_firstshot[i],g_headshot[i],steamid);
			httpClient.Get(url, OnJsonRequest);
		}
	}
}
public Action timer_process(Handle timer)
{
	PrintToChatAll("输入!pause可以暂停 !unpause解除暂停!暂停时间为两分钟");
	Format(url, sizeof(url), "match_api/?request=ping&key=%s&serverid=%s", g_seckey,g_serverid);
	httpClient.Get(url, OnJsonRequest);
}
public Action BanPlayer(Handle timer,DataPack pack){
	char str[64];
	pack.Reset();
	pack.ReadString(str, sizeof(str));

	char iauth[64];
	bool found = false;
	for(int i = 1; i <= MaxClients; i++)
	{
		if (IsValidClient(i)) continue;
		if (!GetClientAuthId(i, AuthId_SteamID64, iauth, sizeof(iauth))) continue;
		if (StrEqual(iauth, str))
		{
			found = true;
			break;
		}
	}
	if(!found){
		Format(url, sizeof(url), "match_api/?request=ban_player&steamid=%s&key=%s&serverid=%s", str,g_seckey,g_serverid);
		httpClient.Get(url, OnJsonRequest);
	}
}
public Action kick_all_player(Handle timer,DataPack pack){
	
	char str[128];
	pack.Reset();
	pack.ReadString(str, sizeof(str));
	for(int i = 1; i <= MaxClients; i++)
	{
		if (IsValidClient(i)) 
			continue;
		KickClient(i, str);
		g_auth[i] = false;
		BanTimers[i] = null;
	}
	InitPlugins();
}

bool CheckInRedTeam(char[] steamid){
	bool found = false;
	for (int i = 0; i < 6; i++){
		if (StrEqual(g_red_team_steamid[i], steamid))
			found = true;
	}
	return found;
}
bool CheckInBlueTeam(char[] steamid){
	bool found = false;
	for (int i = 0; i < 6; i++){
		if (StrEqual(g_blue_team_steamid[i], steamid))
			found = true;
	}
	return found;
}
void stop_pause(){
	ServerCommand("mp_unpause_match");
	PrintToChatAll("暂停时间到!比赛继续!");
	g_pause = 0;
}
public Action stop_pause_timer(Handle timer)
{
	stop_pause();
}
public Action Unpause(int client, int args)
{
	if(g_pause == 0){
		PrintToChat(client,"无法结束暂停!因为不在暂停状态中!");
		return Plugin_Handled;
	}
	int team = g_playerteam[client];
	if (team != g_pause){
		PrintToChat(client,"不是本队发起的暂停无法取消!");
		return Plugin_Handled;
	}
	stop_pause();
	return Plugin_Handled;
}
public Action Pause(int client, int args)
{
	if(g_pause != 0){
		PrintToChat(client,"正在暂停中!无法重复暂停!");
		return Plugin_Handled;
	}
	int team = g_playerteam[client];
	if((team == BLUE_TEAM && g_blue_team_pause) || (team == RED_TEAM && g_red_team_pause)){
		PrintToChat(client,"一个队伍只能暂停一次!");
		return Plugin_Handled;
	}
	if(!g_FreezeTime){
		PrintToChat(client,"比赛中无法暂停请在回合开始时暂停!");
		return Plugin_Handled;
	}
	if(team == BLUE_TEAM)
		g_blue_team_pause = true;
	else
		g_red_team_pause = true;
	g_pause = team;
	ServerCommand("mp_pause_match 2");
	PrintToChatAll("比赛暂停!暂停时间为两分钟!!!");
	PrintToChatAll("比赛暂停!暂停时间为两分钟!!!");
	PrintToChatAll("比赛暂停!暂停时间为两分钟!!!");

	CreateTimer(120.0,stop_pause_timer);
	return Plugin_Handled;
}
void finish_match()
{
	PrintToChatAll("比赛结束!服务器自动关闭!");
	Format(url, sizeof(url), "match_api/?request=post_finish&status=1&key=%s&serverid=%s&red=%d&blue=%d", g_seckey,g_serverid,g_red_team_score,g_blue_team_score);
	httpClient.Get(url, OnJsonRequest);
	DataPack pack;
	CreateDataTimer(5.0, kick_all_player, pack);
	pack.WriteString("比赛结束!服务器自动关闭!");
}
bool UpConfig()
{
	KeyValues kv = new KeyValues("ServerSet");
	char Path[PLATFORM_MAX_PATH];
	BuildPath(Path_SM, Path, sizeof(Path), "configs/crow.ini");
	kv.ImportFromFile(Path);
	if (!kv.JumpToKey("config"))
	{
		return false;
	}
	kv.GetString("api", g_api_addr, 256);
	kv.GetString("id", g_serverid, 256);
	kv.GetString("sec_key", g_seckey, 256);
	httpClient = new HTTPClient(g_api_addr);
	delete kv;
	return true;
}
public Action block(client, args)
{
	return Plugin_Stop;
}  
stock bool IsValidClient(client){
	return (!client || !IsClientConnected(client) || IsFakeClient(client) || client < 1 || client > MaxClients || IsClientSourceTV(client))
}