using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace Steve.TScan {
 public sealed partial class TScanViewer {
  [Serializable] class NewChatRequest {public string request_id;}
  [Serializable] class NewChatResponse {public string archived_run_id,archive_path,new_run_id,error;}
  bool newChatBusy;
  string newChatRequestId="",newChatStatus="",lastChatArchivePath="";
  public string LastChatArchivePath=>lastChatArchivePath;
  public bool NewChatBusy=>newChatBusy;
  public bool StartNewChat(){
   var current=latestFrame??frame;
   if(newChatBusy||sending||current.status=="generating"||current.status=="using_tool"||current.status=="queued")return false;
   StartCoroutine(ArchiveAndNewChat());return true;
  }
  IEnumerator ArchiveAndNewChat(){
   newChatBusy=true;newChatStatus="Archiving this run...";
   yield return FlushOperatorNotes();
   if(!operatorNotesResetReady){newChatStatus="Reset cancelled: your notes have not saved.";newChatBusy=false;yield break;}
   if(string.IsNullOrEmpty(newChatRequestId))newChatRequestId=Guid.NewGuid().ToString("N");
   using(var request=new UnityWebRequest(Endpoint+"/chat/new","POST")){
    request.uploadHandler=new UploadHandlerRaw(Encoding.UTF8.GetBytes(JsonUtility.ToJson(new NewChatRequest{request_id=newChatRequestId})));
    request.downloadHandler=new DownloadHandlerBuffer();request.SetRequestHeader("Content-Type","application/json");request.timeout=30;
    yield return request.SendWebRequest();
    NewChatResponse result=null;
    try{result=JsonUtility.FromJson<NewChatResponse>(request.downloadHandler.text);}catch(Exception){}
    if(request.result==UnityWebRequest.Result.Success&&!string.IsNullOrEmpty(result?.archive_path)){
     lastChatArchivePath=result.archive_path;newChatStatus="Archived. Fresh run ready.";newChatRequestId="";ResetOperatorNotesView();
     chat.Clear();pendingChat=null;activeRequest="";prompt="";chatScroll=Vector2.zero;autoFollowChat=true;
    }else newChatStatus=result?.error??request.error??"Could not archive this run.";
   }
   newChatBusy=false;
  }
 }
}
