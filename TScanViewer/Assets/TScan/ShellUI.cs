using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UIElements;

namespace Steve.TScan {
 // UI Toolkit shell: the world fills the screen; chrome is a Steve card, a mode switch, a few tools, one tabbed rail and
 // a message bar. Steve's reasoning and replies appear as bubbles above him. All data comes from existing viewer state.
 public sealed partial class TScanViewer {
  CharacterHudView characterHud;
  WorldMinimapView watchMinimap;
  UIDocument shDoc;VisualElement shRoot,shCard,shTop,shTools,shMenu,shRail,shPane,shPaneTabs,shChatStack,shDrawer,shMsgs,shBottom,shAnchor,shBubble,shBubBody,shPop,shMem,shRestore,shMemCanvas,shMemDetail,shSegWatch,shSegBuild,shChatBadge,shBubFullBox;
  ScrollView shPaneBody,shMsgScroll,shBubFull;
  Label shBTag,shBText,shBMore,shPopText,shChatStatus,shMemTitle,shMemInfo,shMemSource,shMemKind;
  [SerializeField] string shChatDraft="";
  TextField shSay;VisualElement shPlay,shStopB,shSend;BxIcon shPopIcon,shPlayIcon;
  readonly List<VisualElement> shTrails=new List<VisualElement>();
  readonly Dictionary<string,VisualElement> shTabButtons=new Dictionary<string,VisualElement>();
  readonly Dictionary<string,VisualElement> shMenuItems=new Dictionary<string,VisualElement>();
  readonly List<string> shLog=new List<string>();readonly List<string> shTrailText=new List<string>();
  string shTab="",shPaneKey="",shChatKey="",shLastAction="",shSession="",shLastThought="",shThoughtRequest="",shSpeech="",shMemKey="";
  float shThoughtAt,shSpeechAt;bool shMenuOpen,shDrawerOpen,shBubbleOpen;int shSeenCount;
  [NonSerialized] bool uiInputInitialized;
  readonly Dictionary<string,Vector2> shNodePos=new Dictionary<string,Vector2>();readonly Dictionary<string,Color> shNodeColor=new Dictionary<string,Color>();

  public bool OverUI(Vector2 screen){
   foreach(var root in new[]{shRoot,bxRoot}){
    if(root==null||!root.visible||root.panel==null)continue;
    var p=RuntimePanelUtils.ScreenToPanel(root.panel,new Vector2(screen.x,Screen.height-screen.y));
    var hit=root.panel.Pick(p);
    if(hit!=null&&(hit==root||root.Contains(hit)))return true;
   }
   return false;
  }
  bool UiTyping(){
   foreach(var root in new[]{shRoot,bxRoot}){var f=root?.panel?.focusController?.focusedElement as VisualElement;if(f is TextField||(f!=null&&f.GetFirstAncestorOfType<TextField>()!=null))return true;}
   return false;
  }

  void RemoveUIDocuments(string name){
   foreach(var doc in GetComponentsInChildren<UIDocument>(true))if(doc.gameObject.name==name){
    doc.enabled=false;Destroy(doc.gameObject);
   }
  }
  void EnsureUIInput(){
   // Unity does not rerun EventSystem.Start after a domain reload, but its
   // nonserialized UI Toolkit bridge loses the started flag. Recreate our owned
   // EventSystem once per domain so Start registers the new runtime panels.
   if(!uiInputInitialized){
    foreach(var owned in GetComponentsInChildren<UnityEngine.EventSystems.EventSystem>(true))if(owned.name=="Steve UI Input"){
     owned.gameObject.SetActive(false);Destroy(owned.gameObject);
    }
    uiInputInitialized=true;
   }
   var events=UnityEngine.EventSystems.EventSystem.current;
   if(events==null){
    var go=new GameObject("Steve UI Input");go.transform.SetParent(transform,false);
    events=go.AddComponent<UnityEngine.EventSystems.EventSystem>();
   }
   if(events.GetComponent<UnityEngine.InputSystem.UI.InputSystemUIInputModule>()==null){
    var input=events.gameObject.AddComponent<UnityEngine.InputSystem.UI.InputSystemUIInputModule>();
    input.AssignDefaultActions();
   }
  }
  UIDocument NewUIDoc(string name,int order,out VisualElement root){
   var go=new GameObject(name);go.transform.SetParent(transform,false);go.SetActive(false);
   var ps=ScriptableObject.CreateInstance<PanelSettings>();
   ps.scaleMode=PanelScaleMode.ScaleWithScreenSize;ps.referenceResolution=new Vector2Int(1600,900);ps.screenMatchMode=PanelScreenMatchMode.MatchWidthOrHeight;ps.match=.5f;ps.sortingOrder=order;ps.clearColor=false;
   ps.themeStyleSheet=Resources.Load<ThemeStyleSheet>("UI/SteveTheme");
   var doc=go.AddComponent<UIDocument>();doc.panelSettings=ps;go.SetActive(true);
   var host=doc.rootVisualElement;host.pickingMode=PickingMode.Ignore;
   foreach(var sheet in new[]{"UI/builder","UI/shell","UI/fantasy","UI/character-hud"}){var s=Resources.Load<StyleSheet>(sheet);if(s!=null)host.styleSheets.Add(s);}
   root=BxEl("sv-root",host);root.pickingMode=PickingMode.Ignore;root.style.left=0;root.style.top=0;root.style.right=0;root.style.bottom=0;
   root.style.unityFontDefinition=new StyleFontDefinition(FontDefinition.FromFont(Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf")));
   return doc;
  }
  static void ShClick(VisualElement e,Action act){e.RegisterCallback<ClickEvent>(_=>act());}
  static void ShShow(VisualElement e,bool on){if(e!=null)e.style.display=on?DisplayStyle.Flex:DisplayStyle.None;}
  VisualElement ShIb(VisualElement parent,string icon,Action act){
   var b=BxEl("ib",parent);var ic=new BxIcon(icon){pickingMode=PickingMode.Ignore};ic.AddToClassList("icon");ic.Tint=Muted;b.Add(ic);b.userData=ic;
   b.RegisterCallback<PointerEnterEvent>(_=>{if(!b.ClassListContains("on"))ic.Tint=Bright;});
   b.RegisterCallback<PointerLeaveEvent>(_=>ic.Tint=b.ClassListContains("on")?Teal:Muted);
   ShClick(b,act);return b;
  }
  static void ShSetOn(VisualElement b,bool on){b.EnableInClassList("on",on);if(b.userData is BxIcon ic)ic.Tint=on?Teal:Muted;}

  // ---------- construction ----------
  void ShellCreate(){
   characterHud?.Dispose();EnsureUIInput();RemoveUIDocuments("Shell UI");
   shTrails.Clear();shTabButtons.Clear();shMenuItems.Clear();
   shDoc=NewUIDoc("Shell UI",30,out shRoot);
   characterHud=new CharacterHudView(shRoot,()=>{ShSetMode(true);SetCharacterOpen(true);});shCard=characterHud.Root;
   characterHud.ExpansionChanged+=expanded=>{if(expanded){shDrawerOpen=false;shSay?.Blur();}};
   watchMinimap=new WorldMinimapView(shRoot);
   // mode switch
   shTop=BxEl("topbar glass",shRoot);var seg=BxEl("seg",shTop);
   shSegWatch=BxEl("seg-b",seg);BxLabel("Watch","",shSegWatch);shSegBuild=BxEl("seg-b",seg);BxLabel("Build","",shSegBuild);
   ShClick(shSegWatch,()=>ShSetMode(false));ShClick(shSegBuild,()=>ShSetMode(true));
   // tools
   shTools=BxEl("record-tools",shRoot);
   var chatBtn=ShIb(characterHud.ChatAnchor,"chat",ShToggleChat);chatBtn.AddToClassList("hud-chat-button");chatBtn.name="character-chat-toggle";chatBtn.tooltip="Chat with Steve";
   shChatBadge=BxEl("badge",chatBtn);shChatBadge.pickingMode=PickingMode.Ignore;shChatBadge.style.display=DisplayStyle.None;shTabButtons["_chat"]=chatBtn;
   ShIb(shTools,"cam",ResetCamera);
   var menu=ShIb(shTools,"menu",()=>{shMenuOpen=!shMenuOpen;if(shMenuOpen)shTab="";});shTabButtons["_menu"]=menu;
   // menu
   shMenu=BxEl("menu glass",shRoot);
   ShMenuItem("reset","Reset run","archives",()=>{StartNewChat();shMenuOpen=false;});
   ShMenuItem("orbit","Camera orbit","off",()=>SetOrbit(!OrbitEnabled));
   ShMenuItem("memory","Memory graph","",()=>{SetMemoryFlyout(!memoryFlyout);shMenuOpen=false;});
   ShMenuItem("hide","Hide interface","H",()=>{cinema=true;shMenuOpen=false;});
   // right rail + pane
   shPane=BxEl("pane glass",shRoot);shPaneTabs=BxEl("tabs",shPane);
   shRail=BxEl("record-tabs",shPaneTabs);
   foreach(var t in new[]{("mind","Goals"),("self","Self"),("log","Log"),("debug","Debug")}){var key=t.Item1;var tb=ShIb(shRail,key,()=>{shTab=key;shMenuOpen=false;});tb.tooltip=t.Item2;shTabButtons["tab_"+key]=tb;}
   shPaneTabs.Add(shTools);
   BxButton("×","btn ghost pane-close",()=>shTab="",shPaneTabs).tooltip="Collapse records";
   shPaneBody=new ScrollView(ScrollViewMode.Vertical){verticalScrollerVisibility=ScrollerVisibility.Hidden,horizontalScrollerVisibility=ScrollerVisibility.Hidden};shPaneBody.AddToClassList("pane-body");shPane.Add(shPaneBody);
   // chat drawer
   shChatStack=BxEl("character-chat-stack",shRoot);shChatStack.name="character-chat-stack";
   shDrawer=BxEl("drawer glass",shChatStack);shDrawer.name="steve-chat-pane";BxLabel("CHAT WITH STEVE","label-cap",shDrawer).style.marginBottom=10;
   shMsgScroll=new ScrollView(ScrollViewMode.Vertical){verticalScrollerVisibility=ScrollerVisibility.Hidden,horizontalScrollerVisibility=ScrollerVisibility.Hidden};shMsgScroll.AddToClassList("msgs");shDrawer.Add(shMsgScroll);shMsgs=shMsgScroll.contentContainer;
   shChatStatus=BxLabel("","chat-status",shDrawer);
   // Run/Stop remain available with chat closed. The composer belongs to the chat stack.
   var tr=characterHud.TransportAnchor;
   shPlay=BxEl("play",tr);shPlayIcon=new BxIcon("play"){pickingMode=PickingMode.Ignore};shPlayIcon.AddToClassList("icon");shPlayIcon.Tint=new Color(.16f,.1f,.01f);shPlay.Add(shPlayIcon);
   ShClick(shPlay,()=>{if(!(DashboardBody?.Bench?.State?.running??false))DashboardBody?.Bench?.Resume();});
   shStopB=ShIb(tr,"stop",()=>DashboardBody?.GetComponent<SteveBridge>()?.Pause());shStopB.AddToClassList("stop-b");
   shPlay.name="character-resume";shPlay.tooltip="Resume Steve";shStopB.name="character-stop";shStopB.tooltip="Stop Steve";
   shBottom=BxEl("bottom glass",shChatStack);shBottom.name="steve-chat-composer";
   shSay=new TextField{value=shChatDraft};shSay.AddToClassList("say");shSay.textEdition.placeholder="Tell Steve something…";shSay.textEdition.hidePlaceholderOnFocus=true;shBottom.Add(shSay);
   shSay.RegisterValueChangedCallback(e=>shChatDraft=e.newValue);
   shSay.RegisterCallback<KeyDownEvent>(e=>{if((e.keyCode==KeyCode.Return||e.keyCode==KeyCode.KeypadEnter)&&!e.shiftKey){e.StopPropagation();ShSend();}},TrickleDown.TrickleDown);
   shSend=BxEl("send-b",shBottom);BxLabel("Send","",shSend);ShClick(shSend,ShSend);
   // bubbles anchored to Steve
   shAnchor=BxEl("anchor",shRoot);shAnchor.pickingMode=PickingMode.Ignore;
   for(int i=0;i<2;i++){var tr2=BxEl("trail",shAnchor);tr2.pickingMode=PickingMode.Ignore;var body=BxEl("t",tr2);body.pickingMode=PickingMode.Ignore;BxLabel("","",body);shTrails.Add(tr2);}
   shBubble=BxEl("bubble thought hide",shAnchor);shBubBody=BxEl("bub-body",shBubble);
   var tag=BxEl("bub-tag",shBubBody);BxEl("dot",tag);shBTag=BxLabel("THINKING","",tag);
   shBText=BxLabel("","bub-text",shBubBody);
   shBubFull=new ScrollView(ScrollViewMode.Vertical){verticalScrollerVisibility=ScrollerVisibility.Hidden,horizontalScrollerVisibility=ScrollerVisibility.Hidden};shBubFull.AddToClassList("bub-full");BxLabel("","",shBubFull.contentContainer);shBubBody.Add(shBubFull);
   shBubFullBox=BxLabel("Model-generated explanation, not a record of why he chose. Kept apart from chat and memory.","bub-note",shBubBody);
   shBMore=BxLabel("Click to read it all","bub-more",shBubBody);
   shBubBody.RegisterCallback<ClickEvent>(_=>{shBubbleOpen=!shBubbleOpen;});
   BxEl("stail",shBubble).pickingMode=PickingMode.Ignore;
   var dots=BxEl("dots",shBubble);dots.pickingMode=PickingMode.Ignore;
   foreach(var d in new[]{(-8,0,14),(-3,18,10),(0,32,6)}){var dd=BxEl("d",dots);dd.pickingMode=PickingMode.Ignore;dd.style.left=d.Item1;dd.style.top=d.Item2;dd.style.width=d.Item3;dd.style.height=d.Item3;}
   shPop=BxEl("pop",shAnchor);shPop.pickingMode=PickingMode.Ignore;shPopIcon=new BxIcon("arrow"){pickingMode=PickingMode.Ignore};shPopIcon.AddToClassList("icon");shPopIcon.Tint=Teal;shPop.Add(shPopIcon);shPopText=BxLabel("","",shPop);
   // memory overlay
   shMem=BxEl("mem glass",shRoot);var mh=BxEl("mem-head",shMem);shMemTitle=BxLabel("MEMORY / CONSTELLATION","mem-title",mh);
   var mt=BxEl("tabs",mh);
   var tc=BxEl("tab",mt);BxLabel("Conversation","",tc);ShClick(tc,()=>{developmentGraph=false;selectedMemory="";shMemCanvas.MarkDirtyRepaint();});shTabButtons["mem_c"]=tc;
   var td=BxEl("tab",mt);BxLabel("Development","",td);ShClick(td,()=>{developmentGraph=true;selectedMemory="";shMemCanvas.MarkDirtyRepaint();});shTabButtons["mem_d"]=td;
   var close=ShIb(mh,"close",()=>SetMemoryFlyout(false));
   shMemCanvas=BxEl("mem-canvas",shMem);shMemCanvas.generateVisualContent+=ShPaintMemory;shMemCanvas.RegisterCallback<PointerDownEvent>(ShMemClick);
   shMemDetail=BxEl("mem-detail",shMem);shMemKind=BxLabel("","label-cap",shMemDetail);shMemInfo=BxLabel("","sec-text",shMemDetail);shMemSource=BxLabel("","sec-sub",shMemDetail);
   shMenu.BringToFront();shTools.BringToFront();
   // restore button for hidden-interface mode
   shRestore=BxEl("restore glass",shRoot);BxLabel("Show interface","",shRestore);ShClick(shRestore,()=>cinema=false);
  }
  int chat_Count()=>chat.Count;
  void ShMenuItem(string key,string label,string hint,Action act){
   var item=BxEl("menu-item",shMenu);BxLabel(label,"",item);var h=BxLabel(hint,"mhint",item);item.userData=h;ShClick(item,act);shMenuItems[key]=item;
   if(key=="hide")BxEl("menu-sep",shMenu);
  }
  void ShSetMode(bool build){if(build!=buildOpen)ToggleBuild();shMenuOpen=false;if(build){shDrawerOpen=false;shTab="";}}
  void ShToggleChat(){shDrawerOpen=!shDrawerOpen;shMenuOpen=false;shSeenCount=chat_Count();if(shDrawerOpen)characterHud.SetExpanded(false);else shSay?.Blur();}
  void ShSend(){var text=shSay.value;if(string.IsNullOrWhiteSpace(text))return;if(SubmitChat(text)){shSay.value="";shDrawerOpen=true;}}

  // ---------- frame update ----------
  void UpdateShell(){
   if(shDoc==null||shRoot==null||shRoot.panel==null)ShellCreate();
   var keyboard=Keyboard.current;
   if(keyboard!=null&&!UiTyping()){
    if(keyboard.hKey.wasPressedThisFrame)cinema=!cinema;
    if(keyboard.escapeKey.wasPressedThisFrame){if(memoryFlyout)SetMemoryFlyout(false);else if(characterHud.Expanded)characterHud.SetExpanded(false);else if(shMenuOpen)shMenuOpen=false;else if(shTab!="")shTab="";else if(shDrawerOpen)shDrawerOpen=false;}
   }
   bool watch=!buildOpen&&!cinema;
   shRoot.visible=true;
   ShShow(shCard,watch&&!memoryFlyout);ShShow(shTop,!cinema);ShShow(shRestore,cinema);
   ShShow(shTools,watch);ShShow(shRail,watch);ShShow(shChatStack,watch&&shDrawerOpen&&!memoryFlyout);ShShow(shAnchor,watch&&!memoryFlyout&&DashboardBody?.Bench?.Tool!=null);
   ShShow(shMenu,watch&&shMenuOpen);ShShow(shPane,watch&&!memoryFlyout);ShShow(shPaneBody,shTab!="");ShShow(shMem,memoryFlyout&&!cinema);
   shSegWatch.EnableInClassList("on",!buildOpen);shSegBuild.EnableInClassList("on",buildOpen);
   var f=latestFrame??frame;var grid=DashboardBody?.Bench;var snap=grid?.State;
   // Steve card
   string css;string state=ShState(f,grid,out css);
   characterHud.Update(snap,Connection=="CONNECTED"&&grid!=null&&grid.Ready,state,DashboardBody?.transform,!cinema&&!memoryFlyout);
   ShShow(characterHud.ChatAnchor,watch);ShShow(characterHud.TransportAnchor,watch);
   shChatStack.style.left=shCard.resolvedStyle.left;shChatStack.style.width=shCard.style.width;shChatStack.style.top=shCard.resolvedStyle.top+shCard.style.height.value.value+8;
   ShShow(watchMinimap.Root,watch&&!memoryFlyout);watchMinimap.Update(snap,Connection=="CONNECTED"&&grid!=null&&grid.Ready,builder!=null&&bxDirtyNow);
   shPane.style.top=shTab==""?new StyleLength(StyleKeyword.Auto):new StyleLength(watchMinimap.Root.resolvedStyle.top+watchMinimap.Root.resolvedStyle.height+12);
   shPane.style.height=shTab==""?new StyleLength(62):new StyleLength(StyleKeyword.Auto);
   // tools state
   ShSetOn(shTabButtons["_chat"],shDrawerOpen);ShSetOn(shTabButtons["_menu"],shMenuOpen);
   foreach(var key in new[]{"mind","self","log","debug"})ShSetOn(shTabButtons["tab_"+key],shTab==key);
   var chatLast=chat.Count>0?chat[chat.Count-1]:null;
   shChatBadge.style.display=(!shDrawerOpen&&chat.Count>shSeenCount&&chatLast!=null&&chatLast.role!="user")?DisplayStyle.Flex:DisplayStyle.None;
   if(shDrawerOpen)shSeenCount=chat.Count;
   // menu hints
   ((Label)shMenuItems["orbit"].userData).text=OrbitEnabled?"on":"off";shMenuItems["reset"].EnableInClassList("off",newChatBusy||sending);
   // transport
   bool running=snap?.running??false;
   shPlay.EnableInClassList("off",running);shPlayIcon.Tint=running?new Color(.37f,.45f,.52f):new Color(.16f,.1f,.01f);
   if(shStopB.userData is BxIcon si)si.Tint=running?new Color(1,.48f,.48f):Muted;
   bool online=Connection=="CONNECTED";bool canSend=online&&!sending&&!newChatBusy;shSend.EnableInClassList("off",!canSend);
   if(watch){UpdateDrawer();UpdatePane(f,grid,snap);}
   ShTrackActions(snap);
   ShUpdateBubbleContent(f,grid);
   if(memoryFlyout)ShUpdateMemory();
  }

  string ShState(ScanFrame f,GridWorkbench grid,out string css){
   css="";
   if(Connection!="CONNECTED"){css="bad";return "Offline";}
   string p=grid?.PresentationState;
   if(p=="ORIENTING"||p=="MOVING"||p=="SETTLING")return "Moving";
   if(p=="BLOCKED")return "Blocked";
   if(f.reasoningActive||f.status=="generating")return "Thinking";
   if(f.status=="using_tool")return "Acting";
   if(grid?.State?.running==true)return "Running";
   css="off";return "Idle";
  }

  // ---------- chat drawer ----------
  void UpdateDrawer(){
   if(!shDrawerOpen)return;
   var last=chat.Count>0?chat[chat.Count-1]:null;
   string key=chat.Count+"|"+(last?.text?.Length??0)+"|"+sending+"|"+newChatStatus;
   if(key==shChatKey)return;shChatKey=key;
   shMsgs.Clear();
   if(chat.Count==0)BxLabel("Talk to Steve. He thinks above his head while he works.","sec-sub",shMsgs);
   foreach(var line in chat.ToList()){
    var m=BxEl("m "+(line.role=="user"?"you":line.role=="task"?"task":"steve"),shMsgs);
    BxLabel(line.role=="user"?"YOU":line.role=="task"?"TASK":"STEVE","who",m);
    var t=BxLabel(string.IsNullOrEmpty(line.text)?"…":line.text,"",m);t.enableRichText=false;
   }
   shChatStatus.text=!string.IsNullOrEmpty(newChatStatus)?newChatStatus:sending?"Steve is responding…":Connection=="CONNECTED"?"Connected":"Bridge offline";
   shMsgScroll.schedule.Execute(()=>shMsgScroll.scrollOffset=new Vector2(0,100000)).ExecuteLater(30);
  }

  // ---------- right pane ----------
  VisualElement ShSec(string title,bool gold=false){var s=BxEl("sec");if(!string.IsNullOrEmpty(title))BxLabel(title.ToUpperInvariant(),"sec-title"+(gold?" gold":""),s);return s;}
  void ShTxt(VisualElement p,string text,string cls="sec-text"){if(string.IsNullOrEmpty(text))return;var l=BxLabel(text,cls,p);l.enableRichText=false;}
  void ShKv(VisualElement p,string k,string v){var r=BxEl("kv",p);BxLabel(k,"k",r);var l=BxLabel(v??"","v",r);l.enableRichText=false;}
  void UpdatePane(ScanFrame f,GridWorkbench grid,GridSnapshot snap){
   if(shTab=="")return;
   string key=shTab+"|"+(selfView==null?0:System.Runtime.CompilerServices.RuntimeHelpers.GetHashCode(selfView))+"|"+shLog.Count+"|"+Connection+"|"+f.status+"|"+f.generatedTokens+"|"+(grid?.Error??"")+"|"+(snap?.observation_seq??0);
   if(key==shPaneKey)return;shPaneKey=key;
   var keep=shPaneBody.scrollOffset;var c=shPaneBody.contentContainer;c.Clear();
   if(shTab=="mind")ShBuildGoal(c);else if(shTab=="self")ShBuildSelf(c);else if(shTab=="log")ShBuildLog(c);else ShBuildDebug(c,f,grid,snap);
   shPaneBody.schedule.Execute(()=>shPaneBody.scrollOffset=keep).ExecuteLater(1);
  }
  void ShBuildGoal(VisualElement c){
   if(selfView==null){ShTxt(c,"Connecting…","sec-sub");return;}
   var goal=ShSec("Goal",true);c.Add(goal);
   if(selfView.goals==null||selfView.goals.Length==0)ShTxt(goal,"No goal recorded yet.","sec-sub");
   else foreach(var g in selfView.goals){ShTxt(goal,g.statement,"sec-main");ShTxt(goal,g.reason,"sec-sub");}
   var tasks=ShSec("Tasks");c.Add(tasks);
   if(selfView.tasks==null||selfView.tasks.Length==0)ShTxt(tasks,"No tasks yet.","sec-sub");
   else foreach(var t in selfView.tasks){
    var row=BxEl("task"+(t.status=="completed"?" done":t.in_focus||t.status=="in_progress"?" now":""),tasks);BxEl("ring",row);var l=BxLabel(t.title,"",row);l.enableRichText=false;
   }
   if(selfView.focus!=null&&!string.IsNullOrEmpty(selfView.focus.reason))ShTxt(tasks,selfView.focus.reason,"sec-sub");
   c.tooltip=string.IsNullOrEmpty(selfView.status_note)?"Goal and task statuses are Steve's own assessments, not verified by the world.":selfView.status_note;
  }
  void ShRecords(VisualElement c,string title,SelfRecord[] records,string empty){
   var s=ShSec(title);c.Add(s);
   if(records==null||records.Length==0){ShTxt(s,empty,"sec-sub");return;}
   foreach(var r in records){ShTxt(s,r.statement);ShTxt(s,r.reason,"sec-sub");}
  }
  void ShBuildSelf(VisualElement c){
   if(selfView==null){ShTxt(c,"Connecting…","sec-sub");return;}
   if(selfView.commitments!=null&&selfView.commitments.Length>0)ShRecords(c,"Commitments that persist",selfView.commitments,"");
   ShRecords(c,"Self-assessments",selfView.assessments,"None recorded yet.");
   ShRecords(c,"Beliefs",selfView.beliefs,"None recorded yet.");
   var exp=ShSec("Recent experience");c.Add(exp);
   if(selfView.attempts?.total>0)ShTxt(exp,selfView.attempts.moved+" moves · "+selfView.attempts.blocked+" blocked this run","sec-sub");
   if(selfView.recent==null||selfView.recent.Length==0)ShTxt(exp,"Nothing new recorded.","sec-sub");else foreach(var e in selfView.recent)ShTxt(exp,e.summary);
   var cap=ShSec("Capabilities");c.Add(cap);foreach(var cp in selfView.capabilities??Array.Empty<string>())ShTxt(cap,"• "+cp,"sec-sub");
   if(!string.IsNullOrEmpty(selfError))ShTxt(c,"Connection interrupted. Showing the last state.","note");
  }
  void ShBuildLog(VisualElement c){
   if(shLog.Count==0){ShTxt(c,"Actions Steve takes will be listed here.","sec-sub");return;}
   foreach(var line in shLog){var row=BxEl("logline",c);var parts=line.Split(new[]{'\t'},2);BxLabel(parts[0],"t",row);var l=BxLabel(parts.Length>1?parts[1]:"","",row);l.enableRichText=false;}
  }
  void ShBuildDebug(VisualElement c,ScanFrame f,GridWorkbench grid,GridSnapshot snap){
   var s=ShSec("Connection");c.Add(s);
   ShKv(s,"Bridge",Connection);ShKv(s,"Inference",f.source??"waiting");ShKv(s,"Status",f.status??"");ShKv(s,"Endpoint",Endpoint);
   if(!string.IsNullOrEmpty(grid?.Error))ShKv(s,"Backend error",grid.Error);
   var r=ShSec("Request");c.Add(r);
   ShKv(r,"Request",f.requestId);ShKv(r,"Kind",f.requestKind);ShKv(r,"Output tokens",f.generatedTokens.ToString("N0"));ShKv(r,"Thinking tokens",f.reasoningTokens.ToString("N0"));
   if(snap!=null){var w=ShSec("World");c.Add(w);ShKv(w,"Revision",snap.world_revision.ToString());ShKv(w,"Observation",snap.observation_seq.ToString());ShKv(w,"Session",snap.session_id);ShKv(w,"Presentation",grid.PresentationState);}
   if(!string.IsNullOrEmpty(lastChatArchivePath)){var a=ShSec("Last archive");c.Add(a);ShKv(a,"Path",lastChatArchivePath);}
  }

  // ---------- actions and bubbles ----------
  void ShTrackActions(GridSnapshot snap){
   if(snap==null)return;
   if(snap.session_id!=shSession){shSession=snap.session_id;shLog.Clear();shLastAction="";}
   var r=snap.last_action;if(r==null||string.IsNullOrEmpty(r.action_id)||r.action_id==shLastAction)return;
   shLastAction=r.action_id;
   string name=(r.action??"").Replace("move_","");
   string where=r.position_after!=null&&r.position_after.Length>=2?" to "+r.position_after[0]+", "+r.position_after[1]:"";
   shLog.Insert(0,"#"+r.observation_seq+"\t"+(r.action??"action")+" "+(r.outcome=="moved"?"moved"+where:r.outcome??""));
   if(shLog.Count>60)shLog.RemoveAt(shLog.Count-1);
   shPopText.text=r.outcome=="moved"?name:name+" · "+r.outcome;
   float rot=name=="north"?-90:name=="south"?90:name=="west"?180:0;shPopIcon.style.rotate=new StyleRotate(new Rotate(new Angle(rot,AngleUnit.Degree)));
   shPopIcon.Tint=r.outcome=="moved"?Teal:new Color(1,.48f,.48f);
   shPop.AddToClassList("go");shPop.schedule.Execute(()=>shPop.RemoveFromClassList("go")).ExecuteLater(1600);
  }

  static string ShSnippet(string text,int max){
   text=(text??"").Trim();if(text.Length<=max)return text;
   int cut=text.Length-max;int s=text.IndexOf(". ",cut,StringComparison.Ordinal);
   if(s>=0&&s<text.Length-20)return text.Substring(s+2);
   int sp=text.IndexOf(' ',cut);return "…"+(sp>=0?text.Substring(sp):text.Substring(cut));
  }

  void ShUpdateBubbleContent(ScanFrame f,GridWorkbench grid){
   if(shAnchor==null)return;
   string reasoning=f.reasoningText??"";
   if(f.requestId!=shThoughtRequest){
    if(!string.IsNullOrEmpty(shLastThought)){shTrailText.Insert(0,ShSnippet(shLastThought,70));if(shTrailText.Count>2)shTrailText.RemoveAt(2);}
    shThoughtRequest=f.requestId;shLastThought="";
   }
   if(reasoning.Length>0&&reasoning!=shLastThought){shLastThought=reasoning;shThoughtAt=Time.unscaledTime;}
   var last=chat.LastOrDefault(l=>l.role!="user"&&l.role!="task");
   string spoken=last?.text??"";
   if(spoken.Length>0&&spoken!=shSpeech){shSpeech=spoken;shSpeechAt=Time.unscaledTime;}
   bool thinking=(f.reasoningActive||f.status=="generating")&&shLastThought.Length>0;
   bool speaking=!thinking&&shSpeech.Length>0&&(sending||Time.unscaledTime-shSpeechAt<9f)&&shSpeechAt>=shThoughtAt;
   bool lingering=!thinking&&!speaking&&shLastThought.Length>0&&Time.unscaledTime-shThoughtAt<7f;
   bool show=thinking||speaking||lingering||shBubbleOpen;
   bool speech=speaking&&!shBubbleOpen||(!thinking&&!lingering&&shBubbleOpen&&false);
   shBubble.EnableInClassList("hide",!show);shBubble.EnableInClassList("speech",speech);shBubble.EnableInClassList("thought",!speech);
   shBubble.pickingMode=show?PickingMode.Position:PickingMode.Ignore;
   shBTag.text=speech?"STEVE":thinking?"THINKING":"LAST THOUGHT";
   string text=speech?ShSnippet(shSpeech,220):ShSnippet(shLastThought,200);
   shBText.text=text+(thinking?" ▍":"");shBText.enableRichText=false;
   ShShow(shBText,!shBubbleOpen||speech);
   bool full=shBubbleOpen&&!speech;
   ShShow(shBubFull,full);ShShow(shBubFullBox,full);ShShow(shBMore,show&&!shBubbleOpen&&!speech&&shLastThought.Length>200);
   if(full){var lab=(Label)shBubFull.contentContainer[0];lab.enableRichText=false;if(lab.text!=shLastThought){lab.text=shLastThought;shBubFull.schedule.Execute(()=>shBubFull.scrollOffset=new Vector2(0,100000)).ExecuteLater(30);}}
   for(int i=0;i<shTrails.Count;i++){
    bool have=i<shTrailText.Count&&show&&!speech;ShShow(shTrails[i],have);if(!have)continue;
    ((Label)shTrails[i][0][0]).text=shTrailText[i];
    shTrails[i].style.bottom=100+i*(shBubble.resolvedStyle.height>0?58:58)+(shBubble.resolvedStyle.height>0?shBubble.resolvedStyle.height-40:0);
    shTrails[i].style.scale=new StyleScale(new Scale(new Vector2(.86f-.14f*i,.86f-.14f*i)));shTrails[i].style.opacity=.5f-.2f*i;
   }
  }

  void ShellLateUpdate(){
   if(shDoc==null||shAnchor==null||shRoot==null||shRoot.panel==null)return;
   var body=DashboardBody;var tool=body?.Bench?.Tool;var cam=body?.BodyCamera;if(tool==null||cam==null)return;
   var sp=cam.WorldToScreenPoint(tool.position+Vector3.up*.9f);if(sp.z<0)return;
   var p=RuntimePanelUtils.ScreenToPanel(shRoot.panel,new Vector2(sp.x,Screen.height-sp.y));
   var rect=shRoot.worldBound;
   shAnchor.style.left=p.x-rect.x;shAnchor.style.top=p.y-rect.y;
  }

  // ---------- memory overlay ----------
  void ShUpdateMemory(){
   var graph=memoryGraphs==null?null:(developmentGraph?memoryGraphs.development:memoryGraphs.conversation);
   shMemTitle.text=developmentGraph?"DEVELOPMENT / CONSTELLATION":"MEMORY / CONSTELLATION";
   shTabButtons["mem_c"].EnableInClassList("on",!developmentGraph);shTabButtons["mem_d"].EnableInClassList("on",developmentGraph);
   string key=(developmentGraph?"d":"c")+"|"+(graph==null?0:System.Runtime.CompilerServices.RuntimeHelpers.GetHashCode(graph))+"|"+selectedMemory;
   var sel=graph?.nodes?.FirstOrDefault(n=>n.id==selectedMemory);
   shMemKind.text=sel!=null?(sel.stage??"").Replace('_',' ').ToUpperInvariant():graphConnection+(graph!=null?" | "+graph.record_count+" records":"");
   shMemInfo.text=sel!=null?sel.detail:"Select a light to inspect its record. Lines show recorded category membership. Development proposals are not lived experiences.";
   shMemSource.text=sel!=null?(string.IsNullOrEmpty(sel.source_path)?"":System.IO.Path.GetFileName(sel.source_path)+(sel.source_line>0?" : line "+sel.source_line:"")):"";
   if(key!=shMemKey){shMemKey=key;ShLayoutMemory(graph);shMemCanvas.MarkDirtyRepaint();}
  }
  void ShLayoutMemory(MemoryGraph graph){
   shNodePos.Clear();shNodeColor.Clear();
   foreach(var l in shMemCanvas.Children().Where(c=>c.ClassListContains("mem-hub")).ToList())l.RemoveFromHierarchy();
   if(graph?.nodes==null)return;
   var hubs=graph.nodes.Where(n=>n.hub).ToList();
   for(int i=0;i<hubs.Count;i++){
    float a=i*Mathf.PI*2/Mathf.Max(1,hubs.Count)-Mathf.PI*.5f;var hp=new Vector2(.5f+Mathf.Cos(a)*.34f,.5f+Mathf.Sin(a)*.34f);shNodePos[hubs[i].id]=hp;
    var c=Color.HSVToRGB(Mathf.Repeat((developmentGraph?.08f:.44f)+i*.09f,1),.55f,.95f);shNodeColor[hubs[i].group]=c;
    var children=graph.nodes.Where(n=>!n.hub&&n.group==hubs[i].group).ToList();
    for(int j=0;j<children.Count;j++){float ang=j*2.399963f+i;float spread=(12+Mathf.Sqrt(j+1)*7)/420f;shNodePos[children[j].id]=hp+new Vector2(Mathf.Cos(ang),Mathf.Sin(ang))*spread;}
    var lab=BxLabel((hubs[i].label??"").Replace(" preference","").Replace("historical ",""),"mem-hub",shMemCanvas);lab.style.left=Length.Percent(hp.x*100);lab.style.top=Length.Percent(hp.y*100);
   }
  }
  void ShPaintMemory(MeshGenerationContext ctx){
   var graph=memoryGraphs==null?null:(developmentGraph?memoryGraphs.development:memoryGraphs.conversation);if(graph?.nodes==null||shNodePos.Count==0)return;
   var p=ctx.painter2D;var r=shMemCanvas.contentRect;Vector2 P(Vector2 n)=>new Vector2(n.x*r.width,n.y*r.height);
   p.lineWidth=1;p.strokeColor=new Color(.25f,.55f,.65f,.4f);
   if(graph.edges!=null)foreach(var e in graph.edges)if(shNodePos.TryGetValue(e.source,out var a)&&shNodePos.TryGetValue(e.target,out var b)){p.BeginPath();p.MoveTo(P(a));p.LineTo(P(b));p.Stroke();}
   foreach(var n in graph.nodes){
    if(!shNodePos.TryGetValue(n.id,out var np))continue;var c=shNodeColor.TryGetValue(n.group,out var cc)?cc:Color.white;bool active=selectedMemory==n.id;float size=n.hub?6f:3f;var pos=P(np);
    p.fillColor=new Color(c.r,c.g,c.b,active?.5f:.16f);p.BeginPath();p.Arc(pos,n.hub?20:11,Angle.Degrees(0),Angle.Degrees(360));p.Fill();
    p.fillColor=active?Color.white:c;p.BeginPath();p.Arc(pos,size,Angle.Degrees(0),Angle.Degrees(360));p.Fill();
   }
  }
  void ShMemClick(PointerDownEvent e){
   var r=shMemCanvas.contentRect;string best="";float bd=14;
   foreach(var kv in shNodePos){var d=Vector2.Distance(new Vector2(kv.Value.x*r.width,kv.Value.y*r.height),(Vector2)e.localPosition);if(d<bd){bd=d;best=kv.Key;}}
   selectedMemory=best;shMemKey="";
  }
 }
}
