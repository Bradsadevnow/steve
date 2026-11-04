using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

namespace Steve.TScan {
 public sealed partial class TScanViewer {
  [Serializable] class AgentTask {public string id,title,status;}
  [Serializable] class AgentTaskList {public int revision;public string source,authority,legacy_notes;public AgentTask[] tasks;}
  AgentTaskList agentTasks;
  string agentTasksError="";
  Vector2 agentGoalsScroll;
  GUIStyle agentGoalStyle;
  public int AgentGoalCount=>agentTasks?.tasks?.Length??0;
  IEnumerator PollAgentTasks(){
   while(true){
    int epoch=operatorNotesEpoch;
    using(var request=UnityWebRequest.Get(Endpoint+"/task-list")){
     request.timeout=5;yield return request.SendWebRequest();
     if(epoch==operatorNotesEpoch){
      if(request.result==UnityWebRequest.Result.Success){
       try{var page=JsonUtility.FromJson<AgentTaskList>(request.downloadHandler.text);if(page?.tasks==null)throw new FormatException("Invalid task list");agentTasks=page;agentTasksError="";}catch(Exception error){agentTasksError=error.Message;}
      }else agentTasksError=request.error;
     }
    }
    yield return new WaitForSecondsRealtime(.5f);
   }
  }
  void DrawAgentGoals(float width,float height){
   GUI.Label(new Rect(14,40,width-28,38),"Steve's tasks / statuses reported by Steve",caption);
   if(agentGoalStyle==null)agentGoalStyle=new GUIStyle(chatBody){richText=false};
   float viewHeight=Mathf.Max(30,height-111),textWidth=Mathf.Max(80,width-46),y=0;
   var tasks=agentTasks?.tasks??Array.Empty<AgentTask>();
   float contentHeight=0;foreach(var task in tasks)contentHeight+=26+agentGoalStyle.CalcHeight(new GUIContent(task.title??""),textWidth)+12;
   string legacy=agentTasks?.legacy_notes??"";
   if(!string.IsNullOrEmpty(legacy))contentHeight+=(tasks.Length==0?101:36)+agentGoalStyle.CalcHeight(new GUIContent(legacy),textWidth);
   contentHeight=Mathf.Max(viewHeight,contentHeight);
   agentGoalsScroll=GUI.BeginScrollView(new Rect(12,70,width-24,viewHeight),agentGoalsScroll,new Rect(0,0,textWidth,contentHeight));
   if(tasks.Length==0)GUI.Label(new Rect(0,0,textWidth,50),agentTasks==null?"Waiting for Steve's task list…":"Steve hasn't created any tasks yet.",agentGoalStyle);
   foreach(var task in tasks){
    string status=task.status=="completed"?"COMPLETED":task.status=="in_progress"?"IN PROGRESS":"PENDING";
    GUI.Label(new Rect(0,y,textWidth,22),status,caption);y+=24;
    float h=agentGoalStyle.CalcHeight(new GUIContent(task.title??""),textWidth);GUI.Label(new Rect(0,y,textWidth,h),task.title??"",agentGoalStyle);y+=h+14;
   }
   if(!string.IsNullOrEmpty(legacy)){if(tasks.Length==0)y=65;GUI.Label(new Rect(0,y,textWidth,24),"Earlier working notes",caption);y+=26;GUI.Label(new Rect(0,y,textWidth,agentGoalStyle.CalcHeight(new GUIContent(legacy),textWidth)),legacy,agentGoalStyle);}
   GUI.EndScrollView();
   GUI.Label(new Rect(14,height-32,width-28,28),string.IsNullOrEmpty(agentTasksError)?agentTasks==null?"Connecting…":"Revision "+agentTasks.revision+" / agent-authored":agentTasks==null?"Task list unavailable":"Offline / showing last received tasks",caption);
  }
 }
}
