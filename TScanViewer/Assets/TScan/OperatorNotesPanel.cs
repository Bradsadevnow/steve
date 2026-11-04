using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace Steve.TScan {
 public sealed partial class TScanViewer {
  [Serializable] class OperatorNotesPage {public string run_id,content;public int revision;}
  [Serializable] class OperatorNotesWrite {public string run_id,content;public int expected_revision;}
  string operatorNotesText="",operatorNotesRun="",operatorNotesStatus="Loading notes...";
  int operatorNotesRevision,operatorNotesEpoch;
  bool operatorNotesLoaded,operatorNotesDirty,operatorNotesSaving,operatorNotesConflict,operatorNotesResetReady;
  float operatorNotesEditedAt;
  Vector2 operatorNotesScroll;
  int runNotesTab;
  public string OperatorNotesText=>operatorNotesText;
  public bool OperatorNotesSaved=>operatorNotesLoaded&&!operatorNotesDirty&&!operatorNotesSaving;
  public string OperatorNotesRunId=>operatorNotesRun;
  Rect RunStatusPanel=>new Rect(LedgerPanel.x,LedgerPanel.y,LedgerPanel.width*.5f-4,LedgerPanel.height);
  Rect OperatorNotesPanel=>new Rect(LedgerPanel.x+LedgerPanel.width*.5f+4,LedgerPanel.y,LedgerPanel.width*.5f-4,LedgerPanel.height);

  public void SetOperatorNotes(string value){
   if(!operatorNotesLoaded||newChatBusy)return;
   value=value??"";if(value.Length>65536)value=value.Substring(0,65536);
   if(value==operatorNotesText)return;
   operatorNotesText=value;operatorNotesDirty=true;operatorNotesEditedAt=Time.realtimeSinceStartup;operatorNotesStatus="Unsaved changes";
  }
  IEnumerator PollOperatorNotes(){
   while(true){
    if(operatorNotesDirty&&!operatorNotesConflict&&!operatorNotesSaving&&Time.realtimeSinceStartup-operatorNotesEditedAt>.6f)yield return SaveOperatorNotes();
    else if(!operatorNotesDirty&&!operatorNotesSaving){
     int epoch=operatorNotesEpoch;
     using(var request=UnityWebRequest.Get(Endpoint+"/operator-notes")){
      request.timeout=5;yield return request.SendWebRequest();
      if(epoch==operatorNotesEpoch&&!operatorNotesDirty){
       if(request.result==UnityWebRequest.Result.Success){
        OperatorNotesPage page=null;try{page=JsonUtility.FromJson<OperatorNotesPage>(request.downloadHandler.text);}catch(Exception){}
        if(page!=null&&page.content!=null&&!string.IsNullOrEmpty(page.run_id)){
         operatorNotesText=page.content;operatorNotesRun=page.run_id;operatorNotesRevision=page.revision;operatorNotesLoaded=true;operatorNotesStatus="Saved / this run";
        }
       }else operatorNotesStatus="Notes offline / retrying";
      }
     }
    }
    yield return new WaitForSecondsRealtime(.2f);
   }
  }
  IEnumerator SaveOperatorNotes(){
   operatorNotesSaving=true;string content=operatorNotesText;int epoch=operatorNotesEpoch;operatorNotesStatus="Saving...";
   using(var request=new UnityWebRequest(Endpoint+"/operator-notes","POST")){
    request.uploadHandler=new UploadHandlerRaw(Encoding.UTF8.GetBytes(JsonUtility.ToJson(new OperatorNotesWrite{run_id=operatorNotesRun,expected_revision=operatorNotesRevision,content=content})));
    request.downloadHandler=new DownloadHandlerBuffer();request.SetRequestHeader("Content-Type","application/json");request.timeout=5;
    yield return request.SendWebRequest();
    if(epoch==operatorNotesEpoch){
     OperatorNotesPage page=null;try{page=JsonUtility.FromJson<OperatorNotesPage>(request.downloadHandler.text);}catch(Exception){}
     if(request.result==UnityWebRequest.Result.Success&&page?.run_id==operatorNotesRun&&page.content==content){
      operatorNotesRevision=page.revision;operatorNotesDirty=operatorNotesText!=content;operatorNotesStatus=operatorNotesDirty?"Unsaved changes":"Saved / this run";
     }else{
      operatorNotesConflict=request.responseCode==409;
      operatorNotesStatus=operatorNotesConflict?"Notes changed elsewhere. Copy your draft before reloading.":"Not saved / retrying";
      operatorNotesEditedAt=Time.realtimeSinceStartup+1;
     }
    }
   }
   operatorNotesSaving=false;
  }
  IEnumerator FlushOperatorNotes(){
   while(operatorNotesSaving)yield return null;
   if(operatorNotesDirty&&!operatorNotesConflict)yield return SaveOperatorNotes();
   operatorNotesResetReady=!operatorNotesDirty;
  }
  void ResetOperatorNotesView(){
   operatorNotesEpoch++;operatorNotesLoaded=false;operatorNotesDirty=false;operatorNotesConflict=false;operatorNotesText="";operatorNotesRun="";operatorNotesRevision=0;operatorNotesScroll=Vector2.zero;operatorNotesStatus="Loading notes...";
  }
  void DrawOperatorNotes(){
   var box=OperatorNotesPanel;Fill(box,new Color(.018f,.029f,.039f));GUI.BeginGroup(box);
   float width=box.width;
   runNotesTab=GUI.SelectionGrid(new Rect(12,8,Mathf.Min(width-24,190),28),runNotesTab,new[]{"Notes","Goals"},2,compactButton);
   if(runNotesTab==1){DrawAgentGoals(width,box.height);GUI.EndGroup();return;}
   GUI.Label(new Rect(14,40,width-28,24),"Private to you / archived on Reset / not sent to Steve",caption);
   float viewHeight=Mathf.Max(40,box.height-111),textWidth=Mathf.Max(80,width-46);
   float contentHeight=Mathf.Max(viewHeight-4,fieldStyle.CalcHeight(new GUIContent(operatorNotesText+"\n"),textWidth));
   operatorNotesScroll=GUI.BeginScrollView(new Rect(12,70,width-24,viewHeight),operatorNotesScroll,new Rect(0,0,textWidth,contentHeight));
   GUI.enabled=operatorNotesLoaded&&!newChatBusy;
   SetOperatorNotes(GUI.TextArea(new Rect(0,0,textWidth,contentHeight),operatorNotesText,65536,fieldStyle));GUI.enabled=true;
   GUI.EndScrollView();
   GUI.Label(new Rect(14,box.height-32,width-(operatorNotesConflict?115:28),28),operatorNotesStatus,caption);
   if(operatorNotesConflict&&GUI.Button(new Rect(width-94,box.height-32,80,25),"Reload saved",compactButton))ResetOperatorNotesView();
   GUI.EndGroup();
  }
 }
}
