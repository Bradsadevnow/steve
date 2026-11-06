using System;
using System.Collections.Generic;
using System.Linq;
using System.Collections;
using UnityEngine.Networking;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Steve.TScan
{
    public sealed partial class TScanViewer
    {
        [Serializable] public class ChatMessage {public string role,content,current_token;public bool live;}
        [Serializable] class HistoryResponse {public ChatMessage[] messages;}
        IEnumerator RestoreChat(){
            while(true){using(var req=UnityWebRequest.Get(Endpoint+"/history")){req.timeout=5;yield return req.SendWebRequest();
                if(req.result==UnityWebRequest.Result.Success){var restored=JsonUtility.FromJson<HistoryResponse>(req.downloadHandler.text);if(restored?.messages!=null){chat.Clear();foreach(var m in restored.messages)chat.Add(new ChatLine(m.role,m.content){live=m.live,currentToken=m.current_token});}}
            }yield return new WaitForSecondsRealtime(.4f);}
        }
        sealed class ChatLine {
            public string role,text,currentToken;public bool failed,live;
            public ChatLine(string role,string text){this.role=role;this.text=text;}
        }
        readonly List<ChatLine> chat=new List<ChatLine>();
        readonly List<Texture2D> uiTextures=new List<Texture2D>();
        ChatLine pendingChat;ScanFrame latestFrame;
        bool sending,autoFollowChat=true,memoryFlyout;
        public bool MemoryFlyoutOpen=>memoryFlyout;
        public void SetMemoryFlyout(bool open){memoryFlyout=open;cameraDrag=false;}
        string activeRequest="";
        Vector2 chatScroll,controlScroll,messageScroll;
        bool followMessage=true;string headerRequest="";
        bool cameraDrag,cameraPan,cameraButtonHeld;
        float lastChatHeight;
        GUIStyle chatBody,userBody,roleStyle,tokenStyle,fieldStyle,flatButton,accentButton,compactButton,shortField,caption,heading,muted,liveMessageStyle;
        AvatarCameraRig WorldCamera=>FindFirstObjectByType<SteveBody>()?.EnvironmentCamera;
        public bool OrbitEnabled=>WorldCamera!=null?WorldCamera.OrbitEnabled:false;
        public int ChatMessageCount=>chat.Count;
        public bool ChatIsSending=>sending;
        public string LastChatText=>chat.Count>0?chat[chat.Count-1].text:"";
        public bool SubmitChat(string text){if(sending||string.IsNullOrWhiteSpace(text))return false;prompt=text;StartCoroutine(Generate());return true;}
        float UIScale=>Mathf.Clamp(Screen.height/1000f,.8f,1.6f);
        float CanvasWidth=>Screen.width/UIScale;
        float FullCanvasHeight=>Screen.height/UIScale;
        public string CurrentMessageText=>(latestFrame??frame).text??"";
        float MessageHeight=>0;
        public float MessageBannerPixels=>MessageHeight*UIScale;
        float CanvasHeight=>FullCanvasHeight-MessageHeight;
        float LeftWidth=>Mathf.Clamp(CanvasWidth*.23f,310,390);
        float RightWidth=>Mathf.Clamp(CanvasWidth*.19f,270,325);
        Rect VisualPixels=>cinema?new Rect(0,0,Screen.width,Screen.height):new Rect(LeftWidth*UIScale,0,Screen.width-(LeftWidth+RightWidth)*UIScale,CanvasHeight*UIScale);
        Rect MainVisualPanel=>new Rect(LeftWidth+8,8,CanvasWidth-LeftWidth-RightWidth-16,CanvasHeight-LedgerHeight-24);
        Rect AvatarPanel=>MainVisualPanel;
        Rect ContentPixels(Rect panel)=>new Rect(panel.x*UIScale,(CanvasHeight-panel.yMax)*UIScale,panel.width*UIScale,Mathf.Max(1,panel.height-42)*UIScale);
        Rect Normalized(Rect pixels)=>new Rect(pixels.x/Screen.width,pixels.y/Screen.height,pixels.width/Screen.width,pixels.height/Screen.height);
        public Rect EnvironmentViewport=>new Rect(0,0,1,1);

        Texture2D Swatch(Color color){var t=new Texture2D(1,1);t.SetPixel(0,0,color);t.Apply();uiTextures.Add(t);return t;}
        void UIStyles(){
            var textColor=new Color(.79f,.83f,.87f);
            chatBody=new GUIStyle(GUI.skin.label){fontSize=14,wordWrap=true,richText=false,padding=new RectOffset(0,0,0,0)};
            chatBody.normal.textColor=textColor;
            userBody=new GUIStyle(chatBody);userBody.normal.textColor=Color.white;
            roleStyle=new GUIStyle(chatBody){fontSize=10,fontStyle=FontStyle.Bold};roleStyle.normal.textColor=new Color(.38f,.54f,.63f);
            caption=new GUIStyle(chatBody){fontSize=11};caption.normal.textColor=new Color(.4f,.5f,.58f);
            muted=new GUIStyle(caption){fontSize=12};
            heading=new GUIStyle(chatBody){fontSize=16,fontStyle=FontStyle.Bold};heading.normal.textColor=new Color(.88f,.92f,.95f);
            tokenStyle=new GUIStyle(chatBody){fontSize=30,wordWrap=true};tokenStyle.normal.textColor=new Color(.54f,.88f,.96f);
            liveMessageStyle=new GUIStyle(chatBody){fontSize=16,richText=true,wordWrap=true};liveMessageStyle.normal.textColor=new Color(.86f,.9f,.93f);
            fieldStyle=new GUIStyle(GUI.skin.textArea){fontSize=14,wordWrap=true,padding=new RectOffset(12,12,11,11)};
            var fieldBg=Swatch(new Color(.038f,.052f,.067f));
            fieldStyle.normal.background=fieldBg;fieldStyle.focused.background=fieldBg;
            fieldStyle.normal.textColor=textColor;fieldStyle.focused.textColor=Color.white;
            flatButton=new GUIStyle(GUI.skin.button){fontSize=12,padding=new RectOffset(10,10,8,8),border=new RectOffset(0,0,0,0)};
            flatButton.normal.background=Swatch(new Color(.055f,.072f,.087f));
            flatButton.hover.background=Swatch(new Color(.085f,.12f,.145f));
            flatButton.active.background=Swatch(new Color(.12f,.18f,.21f));
            flatButton.normal.textColor=textColor;flatButton.hover.textColor=Color.white;
            accentButton=new GUIStyle(flatButton);
            accentButton.normal.background=Swatch(new Color(.12f,.34f,.39f));accentButton.normal.textColor=Color.white;
            compactButton=new GUIStyle(flatButton){fontSize=11,padding=new RectOffset(4,4,2,2),alignment=TextAnchor.MiddleCenter};
            compactButton.onNormal.background=accentButton.normal.background;compactButton.onHover.background=accentButton.normal.background;compactButton.onActive.background=accentButton.normal.background;
            compactButton.onNormal.textColor=Color.white;compactButton.onHover.textColor=Color.white;compactButton.onActive.textColor=Color.white;
            shortField=new GUIStyle(fieldStyle){fontSize=13,padding=new RectOffset(8,8,5,5)};
        }
        void Fill(Rect rect,Color color){var old=GUI.color;GUI.color=color;GUI.DrawTexture(rect,Texture2D.whiteTexture);GUI.color=old;}
        static string LiteralMessage(string text)=>text.Replace("<","<\u200B");
        public static string HighlightCurrentToken(string text,string token){
            text=text??"";if(string.IsNullOrEmpty(token))return LiteralMessage(text);
            int at=text.LastIndexOf(token,StringComparison.Ordinal);if(at<0)return LiteralMessage(text);
            string visible=token.Replace("\n","â†µ\n").Replace("\t","â‡¥");
            if(string.IsNullOrWhiteSpace(visible))visible=visible.Replace(" ","Â·");
            return LiteralMessage(text.Substring(0,at))+"<color=#FFD078><b>"+LiteralMessage(visible)+"</b></color>"+LiteralMessage(text.Substring(at+token.Length));
        }
        public string CurrentMessageMarkup {get{var current=latestFrame??frame;string text=current.text??"";if(text.Length==0)return LiteralMessage(string.IsNullOrEmpty(current.error)?"Steve's next message will appear here.":current.error);return HighlightCurrentToken(text,current.token);}}
        void DrawLiveMessage(){
            var current=latestFrame??frame;float width=CanvasWidth,height=MessageHeight;
            Fill(new Rect(0,0,width,height),new Color(.022f,.033f,.043f));
            Fill(new Rect(0,height-1,width,1),new Color(.12f,.25f,.29f));
            GUI.Label(new Rect(20,12,width-40,21),$"CURRENT MESSAGE   /   {current.status??"waiting"}   Â·   token {current.index:0000}   Â·   ID {current.tokenId}",caption);
            if(headerRequest!=current.requestId){headerRequest=current.requestId;messageScroll=Vector2.zero;followMessage=true;}
            float textWidth=Mathf.Max(100,width-56),viewHeight=height-45;
            float contentHeight=Mathf.Max(viewHeight,liveMessageStyle.CalcHeight(new GUIContent(CurrentMessageMarkup),textWidth)+5);
            if(followMessage)messageScroll.y=Mathf.Max(0,contentHeight-viewHeight);
            var before=messageScroll;
            messageScroll=GUI.BeginScrollView(new Rect(20,38,width-32,viewHeight),messageScroll,new Rect(0,0,textWidth,contentHeight));
            GUI.Label(new Rect(0,0,textWidth,contentHeight),CurrentMessageMarkup,liveMessageStyle);GUI.EndScrollView();
            if(Mathf.Abs(messageScroll.y-before.y)>1)followMessage=messageScroll.y>=contentHeight-viewHeight-20;
        }
        void UpdateChatStream(ScanFrame next){
            if(next==null||pendingChat==null||string.IsNullOrEmpty(activeRequest))return;
            if(next.cancelledRequests!=null&&Array.IndexOf(next.cancelledRequests,activeRequest)>=0){pendingChat.failed=true;pendingChat=null;sending=false;return;}
            if(next.requestId!=activeRequest)return;
            if(next.status=="complete"||next.status=="error"){
                pendingChat.failed=next.status=="error";pendingChat=null;sending=false;
            }
        }
        public void SetOrbit(bool enabled){if(WorldCamera!=null)WorldCamera.OrbitEnabled=enabled;cameraDrag=false;}
        bool WorldInputContains(Vector2 point){var viewport=EnvironmentViewport;return !memoryFlyout&&new Rect(viewport.x*Screen.width,viewport.y*Screen.height,viewport.width*Screen.width,viewport.height*Screen.height).Contains(point);}
        public bool CanStartCameraGesture(Vector2 screenPoint)=>!OrbitEnabled&&WorldInputContains(screenPoint);
        public void ResetCamera(){WorldCamera?.ResetView();cameraDrag=false;}
        public void FocusSteve(){WorldCamera?.FocusActor();cameraDrag=false;}
        public object GetCameraState()=>WorldCamera?.State();
        public void ApplyCameraGesture(Vector2 delta,float scrollSteps,bool pan)=>WorldCamera?.ApplyGesture(delta,scrollSteps,pan);
        void HandleCameraInput(){
            var mouse=Mouse.current;if(mouse==null){cameraDrag=false;return;}
            bool inside=WorldInputContains(mouse.position.ReadValue())&&!OverUI(mouse.position.ReadValue());
            bool held=mouse.leftButton.isPressed||mouse.rightButton.isPressed||mouse.middleButton.isPressed;
            bool pressed=held&&!cameraButtonHeld;cameraButtonHeld=held;
            if(inside&&pressed){cameraDrag=!OrbitEnabled;cameraPan=mouse.rightButton.isPressed||mouse.middleButton.isPressed||(Keyboard.current!=null&&(Keyboard.current.leftShiftKey.isPressed||Keyboard.current.rightShiftKey.isPressed));}
            if(buildOpen&&mouse.leftButton.isPressed&&!cameraPan)cameraDrag=false;   // building: left click paints, right/middle drag pans
            if(!held)cameraDrag=false;
            Vector2 delta=cameraDrag?mouse.delta.ReadValue():Vector2.zero;
            float wheel=inside?mouse.scroll.ReadValue().y:0;if(Mathf.Abs(wheel)>10)wheel/=120;
            if(delta!=Vector2.zero)ApplyCameraGesture(delta,0,cameraPan);
            if(wheel!=0)ApplyCameraGesture(Vector2.zero,wheel,false);
        }
        void DrawChat(float width,float height){
            GUI.Label(new Rect(22,22,width-160,27),"Steve",heading);
            var current=latestFrame??frame;
            bool online=Connection=="CONNECTED";
            GUI.enabled=online&&!sending&&!newChatBusy&&current.status!="generating"&&current.status!="using_tool"&&current.status!="queued";
            if(GUI.Button(new Rect(width-116,20,94,28),new GUIContent(newChatBusy?"Archiving...":"Reset","Archive this run, then clear chat and tasks and reset Steve to his starting position."),flatButton))StartNewChat();
            GUI.enabled=true;
            GUI.Label(new Rect(22,55,width-44,36),online?$"{(sending?"Respondingâ€¦":"Connected")}  /  {current.status}\nLM Studio Â· output {current.generatedTokens:N0} tokens reported": "Bridge offline",caption);
            float archiveNotice=string.IsNullOrEmpty(newChatStatus)?0:32;
            if(archiveNotice>0)GUI.Label(new Rect(22,94,width-44,30),new GUIContent(newChatStatus,lastChatArchivePath),caption);
            float viewHeight=Mathf.Max(20,height-250-archiveNotice),textWidth=width-54,labelWidth=textWidth-4;
            var displayed=new List<ChatLine>(chat);
            var heights=new List<float>();var contents=new List<string>();var styles=new List<GUIStyle>();float contentHeight=0;
            foreach(var item in displayed){
                string text=string.IsNullOrEmpty(item.text)?"â€¦":item.text;
                var style=item.live?new GUIStyle(chatBody){richText=true}:item.role=="user"?userBody:chatBody;
                string content=item.live?HighlightCurrentToken(text,item.currentToken??""):text;
                float measured=Mathf.Ceil(style.CalcHeight(new GUIContent(content),labelWidth))+6;
                heights.Add(measured);contents.Add(content);styles.Add(style);contentHeight+=measured+58;
            }
            // Keep a little space after the last reply so its final line can scroll clear.
            contentHeight+=12;
            if(displayed.Count==0)GUI.Label(new Rect(22,112+archiveNotice,width-44,70),"Talk to Steve. Watch the activity unfold beside the conversation.",muted);
            else{
                if(autoFollowChat)chatScroll.y=Mathf.Max(0,contentHeight-viewHeight);
                var before=chatScroll;
                chatScroll=GUI.BeginScrollView(new Rect(18,100+archiveNotice,width-30,viewHeight),chatScroll,new Rect(0,0,textWidth,Mathf.Max(viewHeight,contentHeight)));
                float y=0;
                for(int i=0;i<displayed.Count;i++){
                    var item=displayed[i];GUI.Label(new Rect(4,y,textWidth-4,18),item.role=="user"?"YOU":item.role=="task"?"TASK":"STEVE",roleStyle);
                    GUI.Label(new Rect(4,y+25,labelWidth,heights[i]),contents[i],styles[i]);
                    y+=heights[i]+58;
                }
                GUI.EndScrollView();
                if(Mathf.Abs(chatScroll.y-before.y)>1)autoFollowChat=chatScroll.y>=contentHeight-viewHeight-30;
            }
            GUI.SetNextControlName("ChatInput");
            prompt=GUI.TextArea(new Rect(18,height-142,width-36,80),prompt,fieldStyle);
            bool canSend=online&&!sending&&!newChatBusy&&!string.IsNullOrWhiteSpace(prompt);
            if(Event.current.type==EventType.KeyDown&&Event.current.keyCode==KeyCode.Return&&!Event.current.shift&&GUI.GetNameOfFocusedControl()=="ChatInput"){
                Event.current.Use();if(canSend)StartCoroutine(Generate());
            }
            GUI.enabled=canSend;
            if(GUI.Button(new Rect(18,height-52,width-36,34),sending?"Respondingâ€¦":"Send",accentButton))StartCoroutine(Generate());
            GUI.enabled=true;
        }
        void DrawControls(float x,float width,float height){
            var current=latestFrame??frame;float inset=20,content=width-40;
            controlScroll=GUI.BeginScrollView(new Rect(x+12,24,width-20,Mathf.Max(100,height-88)),controlScroll,new Rect(0,0,content+8,340));
            float y=DrawWorldCameraControls(0,content);
            if(GUI.Button(new Rect(8,y,content,32),"Hide panels",flatButton))cinema=true;y+=48;
            GUI.Label(new Rect(8,y,content,95),"INFERENCE / LM STUDIO\n"+(current.source??"Waiting for server")+"\n"+(current.status??Connection),caption);
            GUI.EndScrollView();
        }
        float DrawWorldCameraControls(float y,float width){
            GUI.Label(new Rect(8,y,width,24),"Avatar camera",heading);y+=38;
            if(GUI.Button(new Rect(8,y,width,34),OrbitEnabled?"Orbit on":"Orbit off Â· manual",OrbitEnabled?accentButton:flatButton))SetOrbit(!OrbitEnabled);y+=46;
            GUI.Label(new Rect(8,y,width,62),OrbitEnabled?"Turn orbit off to explore freely.":"Drag to rotate\nRight / middle drag to pan\nScroll to zoom",muted);y+=76;
            return y;
        }
    }
}
