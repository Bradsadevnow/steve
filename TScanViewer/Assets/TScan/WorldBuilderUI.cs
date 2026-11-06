using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;

namespace Steve.TScan {
 // UI Toolkit view of the world builder: a thumbnail palette, hotbar, tool rail, overview map and apply bar.
 // It owns no world state; every action calls back into the TScanViewer builder fields.
 public sealed partial class TScanViewer {
  static readonly Color Teal=new Color(.82f,.67f,.38f),Gold=new Color(.96f,.73f,.31f),Muted=new Color(.65f,.69f,.71f),Bright=new Color(.95f,.91f,.81f);
  static readonly Dictionary<string,Color> RoleColors=new Dictionary<string,Color>{
   {"floor",new Color32(210,174,114,255)},{"wall",new Color32(132,153,200,255)},{"obstacle",new Color32(230,166,92,255)},
   {"structure",new Color32(170,151,242,255)},{"hazard",new Color32(255,123,123,255)},{"decor",new Color32(127,216,170,255)},{"actor",new Color32(255,111,168,255)},{"boss",new Color32(196,110,255,255)}};
  static readonly Dictionary<string,Color> FlagPaint=new Dictionary<string,Color>{
   {"blue",new Color32(61,139,255,255)},{"red",new Color32(255,77,94,255)},{"yellow",new Color32(255,210,61,255)},{"purple",new Color32(176,108,255,255)},{"orange",new Color32(255,138,42,255)}};
  static readonly string[] RoleOrder={"floor","wall","obstacle","structure","hazard","decor","actor","boss"};
  static readonly Dictionary<string,string> RoleLabel=new Dictionary<string,string>{{"floor","Floors"},{"wall","Walls"},{"obstacle","Objects"},{"structure","Structures"},{"hazard","Hazards"},{"decor","Decor"},{"actor","Enemies"},{"boss","Bosses"}};
  static readonly Dictionary<string,string> RoleOne=new Dictionary<string,string>{{"floor","Floor"},{"wall","Wall"},{"obstacle","Object"},{"structure","Structure"},{"hazard","Hazard"},{"decor","Decor"},{"actor","Enemy"},{"boss","Boss"}};

  UIDocument bxDoc;VisualElement bxStack,bxRoot,bxRail,bxCards,bxHint,bxGrid,bxRoles,bxPacks,bxHotbar,bxSel,bxSelChip,bxToast,bxTip,bxWorlds,bxDraft,bxWorldList,bxWorkspaces,bxOptions;
  Label bxSelName,bxSelectionTitle,bxYaw,bxTipName,bxTipSub,bxToastText,bxDraftText,bxMiniOk;Button bxApply;VisualElement bxSelPic,bxMiniOkBox,bxSwatches,bxMini;BxIcon bxYawIcon,bxOkIcon;TextField bxSaveField;
  readonly Dictionary<BuildTool,VisualElement> bxTools=new Dictionary<BuildTool,VisualElement>();
  readonly Dictionary<BuildTool,Button> bxModeButtons=new Dictionary<BuildTool,Button>();
  readonly Dictionary<string,Texture2D> bxThumbs=new Dictionary<string,Texture2D>();
  readonly List<string> recent=new List<string>();
  readonly List<string> undoStack=new List<string>(),redoStack=new List<string>();
  string bxBaseline="",bxShownStatus="",bxShownPiece="",bxShownRole="",bxShownPack="";BuildTool bxShownTool=(BuildTool)(-1);
  int buildVersion,bxMiniVersion=-1,bxChanges;float bxToastUntil;bool bxDirtyNow;int bxActiveSlot;string bxShownFlag="";

  // ---------- state helpers used by the builder ----------
  string Snap(){return builder==null?"":JsonUtility.ToJson(builder.ToManifest(0));}
  void SetBaseline(){bxBaseline=Snap();buildDraftReload=bxBaseline;undoStack.Clear();redoStack.Clear();bxChanges=0;bxDirtyNow=false;buildVersion++;}
  void PushUndo(){undoStack.Add(Snap());if(undoStack.Count>120)undoStack.RemoveAt(0);redoStack.Clear();}
  void AfterEdit(){
   buildDraftReload=Snap();
   var lost=builder.Unreachable();buildStatus=lost??"";buildProblem=lost!=null;
   buildVersion++;RefreshDirty();
  }
  void RefreshDirty(){var now=Snap();bxDirtyNow=now!=bxBaseline;bxChanges=bxDirtyNow?undoStack.Count:0;}
  void Undo(){if(undoStack.Count==0)return;redoStack.Add(Snap());builder.Load(JsonUtility.FromJson<MeadowManifest>(undoStack[undoStack.Count-1]));undoStack.RemoveAt(undoStack.Count-1);RefreshPreview();AfterEdit();}
  void Redo(){if(redoStack.Count==0)return;undoStack.Add(Snap());builder.Load(JsonUtility.FromJson<MeadowManifest>(redoStack[redoStack.Count-1]));redoStack.RemoveAt(redoStack.Count-1);RefreshPreview();AfterEdit();}
  void SelectPiece(string id,bool fromSlot=false){
   selectedPiece=id;buildTool=BuildTool.Piece;
   if(!fromSlot){recent.Remove(id);recent.Insert(0,id);if(recent.Count>9)recent.RemoveAt(9);bxActiveSlot=0;}
   BxRefreshPalette();BxRefreshHotbar();
  }
  void TogglePieces(){bxStack.style.display=bxStack.style.display==DisplayStyle.None?DisplayStyle.Flex:DisplayStyle.None;BxHideTip();}
  void SelectSlot(int index){if(index<0||index>=recent.Count)return;bxActiveSlot=index;SelectPiece(recent[index],true);}
  void RotateYaw(int delta){buildYaw=((buildYaw+delta)%360+360)%360;}
  void SelectBuildTool(BuildTool tool){
   buildTool=tool;if(bxStack!=null)bxStack.style.display=DisplayStyle.Flex;
   BxRefreshPalette();BxHideTip();
  }
  public bool OverBuildUI(Vector2 screen){
   if(bxDoc==null||bxRoot==null||!bxRoot.visible||bxRoot.panel==null)return false;
   var p=RuntimePanelUtils.ScreenToPanel(bxRoot.panel,new Vector2(screen.x,Screen.height-screen.y));
   return bxRoot.panel.Pick(p)!=null;
  }
  bool BxTyping()=>UiTyping();

  // ---------- element helpers ----------
  static VisualElement BxEl(string cls,VisualElement parent=null){var e=new VisualElement();foreach(var c in cls.Split(' '))if(c.Length>0)e.AddToClassList(c);parent?.Add(e);return e;}
  static Label BxLabel(string text,string cls,VisualElement parent=null){var l=new Label(text){pickingMode=PickingMode.Ignore};foreach(var c in cls.Split(' '))if(c.Length>0)l.AddToClassList(c);parent?.Add(l);return l;}
  static Button BxButton(string text,string cls,Action click,VisualElement parent=null){var b=new Button(click){text=text};b.style.backgroundColor=StyleKeyword.Null;foreach(var c in cls.Split(' '))if(c.Length>0)b.AddToClassList(c);b.style.borderTopWidth=b.style.borderBottomWidth=b.style.borderLeftWidth=b.style.borderRightWidth=cls.Contains("ghost")?1:0;parent?.Add(b);return b;}
  Texture2D Thumb(string id){if(!bxThumbs.TryGetValue(id,out var t)){t=Resources.Load<Texture2D>("Meadow/kit/thumbs/"+id);bxThumbs[id]=t;}return t;}
  void SetPic(VisualElement e,string id){var t=string.IsNullOrEmpty(id)?null:Thumb(id);e.style.backgroundImage=t!=null?new StyleBackground(t):new StyleBackground(StyleKeyword.None);}
  static Color RoleColor(string role)=>RoleColors.TryGetValue(role??"",out var c)?c:Muted;

  // ---------- construction ----------
  void BxCreate(){
   HideModuleTooltip();moduleInspectPreview?.Dispose();moduleInspectPreview=null;DestroyCharacterStage();characterKey="";
   EnsureUIInput();RemoveUIDocuments("Builder UI");bxTools.Clear();bxModeButtons.Clear();
   var go=new GameObject("Builder UI");go.transform.SetParent(transform,false);go.SetActive(false);
   var ps=ScriptableObject.CreateInstance<PanelSettings>();
   ps.scaleMode=PanelScaleMode.ScaleWithScreenSize;ps.referenceResolution=new Vector2Int(1600,900);ps.screenMatchMode=PanelScreenMatchMode.MatchWidthOrHeight;ps.match=.5f;ps.sortingOrder=20;ps.clearColor=false;ps.themeStyleSheet=Resources.Load<ThemeStyleSheet>("UI/SteveTheme");
   bxDoc=go.AddComponent<UIDocument>();bxDoc.panelSettings=ps;go.SetActive(true);
   var sheet=Resources.Load<StyleSheet>("UI/builder");
   var root=bxDoc.rootVisualElement;root.pickingMode=PickingMode.Ignore;if(sheet!=null)root.styleSheets.Add(sheet);root.styleSheets.Add(Resources.Load<StyleSheet>("UI/fantasy"));
   bxRoot=BxEl("sv-root",root);bxRoot.pickingMode=PickingMode.Ignore;
   bxRoot.style.unityFontDefinition=new StyleFontDefinition(FontDefinition.FromFont(Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf")));
   BxBuildRail();BxBuildMini();BxBuildDock();BuildCharacterPanel();
   bxWorkspaces=BxEl("workspaces glass",bxRoot);bxWorkspaces.name="builder-workspace-tabs";
   BxButton("World","btn ghost workspace-tab",()=>SetCharacterOpen(false),bxWorkspaces).name="workspace-world";
   BxButton("Character","btn ghost workspace-tab",()=>SetCharacterOpen(true),bxWorkspaces).name="workspace-character";
   bxTip=BxEl("tip",bxRoot);bxTip.pickingMode=PickingMode.Ignore;bxTipName=BxLabel("","tip-name",bxTip);bxTipSub=BxLabel("","tip-sub",bxTip);
   bxToast=BxEl("toast glass",bxRoot);bxToast.pickingMode=PickingMode.Ignore;bxToastText=BxLabel("","",bxToast);
   BxRefreshAll();
  }

  void BxBuildRail(){
   bxRail=BxEl("rail glass",bxRoot);
   BxAddAction("undo","Ctrl Z","Undo",Undo);BxAddAction("redo","Ctrl Y","Redo",Redo);BxAddAction("rotate","R","Rotate piece",()=>RotateYaw(90));
  }
  void BxAddTool(BuildTool tool,string icon,string key,string tip){
   var b=BxToolButton(icon,key,tip,()=>SelectBuildTool(tool));bxTools[tool]=b;
  }
  void BxAddAction(string icon,string key,string tip,Action act)=>BxToolButton(icon,key,tip,act);
  VisualElement BxToolButton(string icon,string key,string tip,Action act){
   var b=BxEl("tool",bxRail);var ic=new BxIcon(icon){pickingMode=PickingMode.Ignore};ic.AddToClassList("icon");b.Add(ic);BxLabel(key.Length<=2?key:"","kbd",b);
   b.userData=ic;ic.Tint=Muted;
   b.RegisterCallback<ClickEvent>(_=>act());
   b.RegisterCallback<PointerEnterEvent>(_=>{BxShowTip(b,tip,key,true);if(!b.ClassListContains("on"))ic.Tint=Bright;});
   b.RegisterCallback<PointerLeaveEvent>(_=>{BxHideTip();ic.Tint=b.ClassListContains("on")?Teal:Muted;});
   return b;
  }

  void BxBuildMini(){
   var mini=BxEl("mini glass",bxRoot);bxMini=mini;
   var head=BxEl("mini-head",mini);BxLabel("OVERVIEW","label-cap",head);BxLabel("15 × 15","label-cap",head);
   var map=BxEl("mini-map",mini);map.generateVisualContent+=BxPaintMap;bxMiniOkBox=map;
   var ok=BxEl("mini-ok",mini);bxMiniOk=BxLabel("","",ok);bxOkIcon=new BxIcon("check"){pickingMode=PickingMode.Ignore};bxOkIcon.AddToClassList("icon");ok.Insert(0,bxOkIcon);bxMini=ok;
  }

  void BxBuildDock(){
   var dock=BxEl("dock",bxRoot);dock.pickingMode=PickingMode.Ignore;
   bxOptions=BxEl("world-options glass",dock);bxOptions.name="world-builder-options";
   var optionScroll=new ScrollView(ScrollViewMode.Vertical){horizontalScrollerVisibility=ScrollerVisibility.Hidden};optionScroll.AddToClassList("world-options-scroll");bxOptions.Add(optionScroll);
   var options=optionScroll.contentContainer;
   bxStack=BxEl("stack",dock);
   var pal=BxEl("palette glass",bxStack);pal.name="world-builder-assets";BxLabel("ASSET LIBRARY","sec-title",pal);
   bxHotbar=BxEl("hotbar glass",bxStack);
   for(int i=0;i<9;i++){
    int index=i;var slot=BxEl("slot",bxHotbar);BxLabel((i+1).ToString(),"num",slot);var pic=BxEl("pic",slot);pic.pickingMode=PickingMode.Ignore;
    slot.RegisterCallback<ClickEvent>(_=>SelectSlot(index));
    slot.RegisterCallback<PointerEnterEvent>(_=>{if(index<recent.Count){var info=WorldKit.Info(recent[index]);if(info!=null)BxShowTip(slot,info.name,BxRoleLine(info),false);}});
    slot.RegisterCallback<PointerLeaveEvent>(_=>BxHideTip());
   }
   BxLabel("TOOLS","label-cap",options);var modes=BxEl("build-modes",options);
   void Mode(BuildTool tool,string label,string name){
    var button=BxButton(label,"btn ghost mode-button",()=>SelectBuildTool(tool),modes);
    button.name=name;bxModeButtons[tool]=button;
   }
   Mode(BuildTool.Piece,"Pieces · B","builder-pieces");
   Mode(BuildTool.Spawn,"Start · P","builder-start");
   Mode(BuildTool.Flag,"Flags · F","builder-flags");
   Mode(BuildTool.Erase,"Delete · X","builder-delete");
   var filters=BxEl("filters",options);BxLabel("CATEGORIES","label-cap",filters);bxRoles=BxEl("chips",filters);BxLabel("ASSET KITS","label-cap",filters);bxPacks=BxEl("chips",filters);
   bxGrid=new ScrollView(ScrollViewMode.Vertical){verticalScrollerVisibility=ScrollerVisibility.Auto,horizontalScrollerVisibility=ScrollerVisibility.Hidden};bxGrid.AddToClassList("grid");pal.Add(bxGrid);
   bxCards=BxEl("cards",((ScrollView)bxGrid).contentContainer);
   bxHint=BxEl("hint",options);bxHint.style.display=DisplayStyle.None;bxSwatches=BxEl("swatches",bxHint);
   var overview=new Foldout{text="World overview",value=false};options.Add(overview);overview.Add(bxRoot.Q(className:"mini"));
   bxOptions.Add(bxRail);
   var actions=BxEl("actions",bxOptions);
   var inspector=BxEl("selection-inspector glass",dock);inspector.name="builder-selection-inspector";
   bxSelectionTitle=BxLabel("SELECTED ASSET","label-cap",inspector);
   bxSel=BxEl("sel",inspector);bxSelPic=BxEl("pic",bxSel);var col=BxEl("selection-description",bxSel);bxSelName=BxLabel("","sel-name",col);
   var row=BxEl("sel-row",col);bxSelChip=BxEl("chip",row);BxEl("dot",bxSelChip);BxLabel("","",bxSelChip);
   var yaw=BxEl("yaw",row);bxYawIcon=new BxIcon("rotate"){pickingMode=PickingMode.Ignore};bxYawIcon.AddToClassList("icon");bxYawIcon.Tint=Muted;yaw.Add(bxYawIcon);bxYaw=BxLabel("0°","",yaw);
   bxDraft=BxEl("draft",actions);BxEl("dot",bxDraft);bxDraftText=BxLabel("","",bxDraft);
   BxButton("Assets","btn ghost",()=>TogglePieces(),actions);
   BxButton("Worlds","btn ghost",()=>{bxWorlds.style.display=bxWorlds.style.display==DisplayStyle.None?DisplayStyle.Flex:DisplayStyle.None;BxFillWorlds();},actions);
   BxButton("Revert","btn ghost",RevertBuild,actions);
   bxApply=BxButton("Apply to world","btn primary",()=>{if(bxDirtyNow||buildVersion==0)ApplyBuild();},actions);
   bxWorlds=BxEl("worlds glass",actions);bxWorlds.style.display=DisplayStyle.None;
   BxLabel("WORLDS","label-cap",bxWorlds);
   var wr=BxEl("worlds-row",bxWorlds);bxSaveField=new TextField{value=saveName,maxLength=40};wr.Add(bxSaveField);
   bxSaveField.RegisterValueChangedCallback(e=>saveName=e.newValue);
   BxButton("Save","btn primary",()=>{var file=builder.Save(saveName,buildEnv.definition.manifest.revision);savedWorlds=WorldBuilder.SavedNames();buildStatus="Saved "+file;buildProblem=false;BxFillWorlds();},wr);
   bxWorldList=BxEl("",bxWorlds);bxWorldList.style.marginTop=8;
  }

  void BxFillWorlds(){
   bxWorldList.Clear();savedWorlds=WorldBuilder.SavedNames();
   foreach(var name in savedWorlds.Take(6)){
    var n=name;var item=BxEl("world-item",bxWorldList);BxLabel(n,"",item);
    item.RegisterCallback<ClickEvent>(_=>{
     PushUndo();
     if(builder.TryLoad(n,out var why)){RefreshPreview();saveName=n;bxSaveField.SetValueWithoutNotify(n);buildStatus="Loaded "+n+" as a draft.";buildProblem=false;AfterEdit();bxWorlds.style.display=DisplayStyle.None;}
     else{undoStack.RemoveAt(undoStack.Count-1);buildStatus=why;buildProblem=true;}
    });
   }
   if(savedWorlds.Length==0)BxLabel("No saved worlds yet.","mono",bxWorldList);
  }

  // ---------- refresh ----------
  static string BxRoleLine(KitPieceInfo info)=>RoleOne[WorldKit.CategoryOf(info)]+(info.blocks?"  ·  blocks movement":"  ·  walkable")+(WorldKit.FootprintOf(info)>1?"  ·  "+WorldKit.FootprintOf(info)+" × "+WorldKit.FootprintOf(info)+" cells":"");
  void BxShowTip(VisualElement anchor,string name,string sub,bool side){
   bxTipName.text=name;bxTipSub.text=sub;bxTip.AddToClassList("show");
   var a=anchor.worldBound;var r=bxRoot.worldBound;
   bxTip.style.left=side?a.xMax-r.x+78:a.center.x-r.x;bxTip.style.top=side?a.center.y-r.y+18:a.y-r.y-8;
   bxTip.style.translate=side?new StyleTranslate(new Translate(0,0)):new StyleTranslate(new Translate(Length.Percent(-50),Length.Percent(-100)));
  }
  void BxHideTip(){bxTip?.RemoveFromClassList("show");}

  void BxRefreshAll(){BxRefreshPalette();BxRefreshHotbar();}
  void BxRefreshHotbar(){
   bxHotbar.style.display=recent.Count==0||buildTool!=BuildTool.Piece?DisplayStyle.None:DisplayStyle.Flex;
   var slots=bxHotbar.Children().ToList();
   for(int i=0;i<slots.Count;i++){
    var id=i<recent.Count?recent[i]:null;slots[i].EnableInClassList("filled",id!=null);slots[i].EnableInClassList("active",id!=null&&i==bxActiveSlot&&buildTool==BuildTool.Piece&&id==selectedPiece);
    SetPic(slots[i].Q(className:"pic"),id);
   }
  }

  void BxRefreshPalette(){
   bxShownRole=roleFilter;bxShownPack=packFilter;bxShownTool=buildTool;bxShownPiece=selectedPiece;bxShownFlag=flagColor;
   foreach(var kv in bxTools){kv.Value.EnableInClassList("on",kv.Key==buildTool);((BxIcon)kv.Value.userData).Tint=kv.Key==buildTool?Teal:Muted;}
   foreach(var kv in bxModeButtons)kv.Value.EnableInClassList("on",kv.Key==buildTool);
   bool piece=buildTool==BuildTool.Piece;
   bxGrid.style.display=piece?DisplayStyle.Flex:DisplayStyle.None;bxRoles.parent.style.display=piece?DisplayStyle.Flex:DisplayStyle.None;
   bxHint.style.display=piece?DisplayStyle.None:DisplayStyle.Flex;
   bxSwatches.style.display=buildTool==BuildTool.Flag?DisplayStyle.Flex:DisplayStyle.None;
   if(!piece){
    bxHint.Clear();bxSwatches=BxEl("swatches",bxHint);
    var text=buildTool==BuildTool.Flag?"Click a cell to place or move this flag. Every flag must stay reachable."
     :buildTool==BuildTool.Spawn?"Click a valid cell, then Apply to move Steve there and save his start. Draft edits do not move him until applied."
     :"Click an object or flag to delete it. Undo restores it. Hold ½ second and drag to rotate the camera.";
    var l=BxLabel(text,"",bxHint);bxHint.Insert(0,l);
    if(buildTool==BuildTool.Flag)foreach(var c in WorldBuilder.FlagColors){
     var color=c;var sw=BxEl("swatch",bxSwatches);sw.style.backgroundColor=FlagPaint[c];sw.EnableInClassList("on",flagColor==c);
     sw.name="builder-flag-"+c;sw.tooltip="Place or move the "+c+" flag";
     var label=BxLabel(char.ToUpperInvariant(c[0])+c.Substring(1),"swatch-name",sw);
     label.style.color=c=="blue"||c=="purple"?Color.white:new Color(.08f,.1f,.14f);
     sw.RegisterCallback<ClickEvent>(_=>{flagColor=color;BxRefreshPalette();});
    }else bxSwatches.style.display=DisplayStyle.None;
   }else{
    var usable=WorldKit.Pieces.Where(WorldKit.IsPlaceable).ToList();
    bxRoles.Clear();
    var inPack=usable.Where(p=>packFilter==""||p.pack==packFilter).ToList();
    foreach(var role in RoleOrder){
     var r=role;var chip=BxEl("role",bxRoles);chip.EnableInClassList("on",roleFilter==r);var dot=BxEl("dot",chip);dot.style.backgroundColor=RoleColor(r);dot.pickingMode=PickingMode.Ignore;
     BxLabel(RoleLabel[r],"",chip);BxLabel(inPack.Count(p=>WorldKit.CategoryOf(p)==r).ToString(),"count",chip);
     if(roleFilter==r)chip.style.borderTopColor=chip.style.borderBottomColor=chip.style.borderLeftColor=chip.style.borderRightColor=RoleColor(r);
     chip.RegisterCallback<ClickEvent>(_=>{roleFilter=roleFilter==r?"":r;BxRefreshPalette();});
    }
    bxPacks.Clear();
    var packs=WorldKit.Packs.Where(p=>usable.Any(q=>q.pack==p)).ToList();packs.Insert(0,"");
    foreach(var pack in packs){
     var k=pack;var chip=BxEl("pack",bxPacks);chip.EnableInClassList("on",packFilter==k);BxLabel(k==""?"All kits":ShortPack(k),"",chip);
     chip.RegisterCallback<ClickEvent>(_=>{packFilter=k;BxRefreshPalette();});
    }
    var list=usable.Where(p=>(roleFilter==""||WorldKit.CategoryOf(p)==roleFilter)&&(packFilter==""||p.pack==packFilter)).OrderBy(p=>RoleRank(WorldKit.CategoryOf(p))).ThenBy(p=>p.name).ToList();
    bxCards.Clear();
    foreach(var p in list){
     var info=p;var card=BxEl("card",bxCards);card.EnableInClassList("on",selectedPiece==info.id);
     var pic=BxEl("pic",card);pic.pickingMode=PickingMode.Ignore;SetPic(pic,info.id);
     var bar=BxEl("bar",card);bar.style.backgroundColor=RoleColor(WorldKit.CategoryOf(info));bar.pickingMode=PickingMode.Ignore;
     if(info.blocks){var s=new BxIcon("shield"){pickingMode=PickingMode.Ignore};s.AddToClassList("blocks");s.Tint=Muted;card.Add(s);}
     card.RegisterCallback<ClickEvent>(_=>SelectPiece(info.id));
     card.RegisterCallback<PointerEnterEvent>(_=>BxShowTip(card,info.name,BxRoleLine(info),false));
     card.RegisterCallback<PointerLeaveEvent>(_=>BxHideTip());
    }
   }
   BxRefreshSelection();BxRefreshHotbar();
  }

  void BxRefreshSelection(){
   var info=WorldKit.Info(selectedPiece);bool piece=buildTool==BuildTool.Piece&&info!=null;
   bxSelectionTitle.text=piece?"SELECTED ASSET":"ACTIVE TOOL";
   if(piece){
    SetPic(bxSelPic,info.id);bxSelName.text=info.name;
    ((Label)bxSelChip[1]).text=RoleOne[WorldKit.CategoryOf(info)]+(info.blocks?" · blocks":" · walkable");bxSelChip[0].style.backgroundColor=RoleColor(WorldKit.CategoryOf(info));
    bxSelChip.style.display=DisplayStyle.Flex;
   }else{
    bxSelPic.style.backgroundImage=new StyleBackground(StyleKeyword.None);
    bxSelName.text=buildTool==BuildTool.Spawn?"Steve's start":buildTool==BuildTool.Flag?char.ToUpperInvariant(flagColor[0])+flagColor.Substring(1)+" flag":"Delete tool";
    bxSelChip.style.display=DisplayStyle.None;
   }
  }

  void BxPaintMap(MeshGenerationContext ctx){
   if(builder==null)return;
   var p=ctx.painter2D;var r=bxMiniOkBox.contentRect;float n=WorldBuilder.Size,s=Mathf.Min(r.width,r.height)/n,ox=(r.width-s*n)/2,oy=(r.height-s*n)/2;
   for(int i=0;i<WorldBuilder.Size;i++)for(int j=0;j<WorldBuilder.Size;j++){
    BxRect(p,ox+i*s,oy+j*s,s,s,(i+j)%2==0?new Color(.055f,.095f,.14f):new Color(.07f,.11f,.16f));
   }
   void Cell(MeadowPlacement m){var info=WorldKit.Info(m.prototype);if(info==null)return;int h=WorldKit.FootprintOf(info)/2;float side=(2*h+1)*s;BxRect(p,ox+(m.col-1-h)*s+1.5f,oy+(WorldBuilder.Size-m.row-h)*s+1.5f,side-3,side-3,RoleColor(WorldKit.CategoryOf(info)));}
   foreach(var o in builder.Obstacles)Cell(o);foreach(var pr in builder.Props)Cell(pr);
   foreach(var f in builder.Landmarks){
    p.fillColor=FlagPaint.TryGetValue(f.color??"",out var fc)?fc:Bright;p.BeginPath();p.Arc(new Vector2(ox+(f.col-.5f)*s,oy+(WorldBuilder.Size-f.row+.5f)*s),s*.3f,Angle.Degrees(0),Angle.Degrees(360));p.Fill();
    p.strokeColor=new Color(1,1,1,.7f);p.lineWidth=1.2f;p.Stroke();
   }
   var sc=new Vector2(ox+(builder.Spawn.col-.5f)*s,oy+(WorldBuilder.Size-builder.Spawn.row+.5f)*s);
   p.strokeColor=Teal;p.lineWidth=2.2f;p.BeginPath();p.Arc(sc,s*.38f,Angle.Degrees(0),Angle.Degrees(360));p.Stroke();
   p.fillColor=Teal;p.BeginPath();p.Arc(sc,s*.13f,Angle.Degrees(0),Angle.Degrees(360));p.Fill();
   if(hoverCell){p.strokeColor=hoverValid?Teal:new Color(1,.3f,.3f);p.lineWidth=1.6f;p.BeginPath();p.MoveTo(new Vector2(ox+(hoverCol-1)*s,oy+(WorldBuilder.Size-hoverRow)*s));p.LineTo(new Vector2(ox+hoverCol*s,oy+(WorldBuilder.Size-hoverRow)*s));p.LineTo(new Vector2(ox+hoverCol*s,oy+(WorldBuilder.Size-hoverRow+1)*s));p.LineTo(new Vector2(ox+(hoverCol-1)*s,oy+(WorldBuilder.Size-hoverRow+1)*s));p.ClosePath();p.Stroke();}
  }
  static void BxRect(Painter2D p,float x,float y,float w,float h,Color c){p.fillColor=c;p.BeginPath();p.MoveTo(new Vector2(x,y));p.LineTo(new Vector2(x+w,y));p.LineTo(new Vector2(x+w,y+h));p.LineTo(new Vector2(x,y+h));p.ClosePath();p.Fill();}

  // ---------- per frame ----------
  void UpdateBuildUI(){
   bool show=buildOpen&&builder!=null&&!memoryFlyout&&!cinema;
   if(!show){if(bxRoot!=null)bxRoot.visible=false;if(characterStage)DestroyCharacterStage();return;}
   if(bxDoc==null||bxRoot==null||bxRoot.panel==null)BxCreate();
   bxRoot.visible=true;
   var tabParent=characterOpen?characterPanel:bxOptions;if(bxWorkspaces.parent!=tabParent)tabParent.Add(bxWorkspaces);
   bxWorkspaces.EnableInClassList("world-workspaces",!characterOpen);
   bxWorkspaces.Q<Button>("workspace-world").EnableInClassList("on",!characterOpen);bxWorkspaces.Q<Button>("workspace-character").EnableInClassList("on",characterOpen);
   if(buildTool==BuildTool.Spawn)bxSelName.text="Steve's start · ("+builder.Spawn.col+", "+builder.Spawn.row+")";
   UpdateCharacterUI();
   foreach(var child in bxRoot.Children())if(child.ClassListContains("rail")||child.ClassListContains("mini")||child.ClassListContains("dock"))child.style.display=characterOpen?DisplayStyle.None:DisplayStyle.Flex;
   var vp=EnvironmentViewport;var panel=bxRoot.panel;
   if(panel!=null){
    var tl=RuntimePanelUtils.ScreenToPanel(panel,new Vector2(vp.x*Screen.width,Screen.height-(vp.y+vp.height)*Screen.height));
    var br=RuntimePanelUtils.ScreenToPanel(panel,new Vector2((vp.x+vp.width)*Screen.width,Screen.height-vp.y*Screen.height));
    bxRoot.style.left=tl.x;bxRoot.style.top=tl.y;bxRoot.style.width=br.x-tl.x;bxRoot.style.height=br.y-tl.y;
   }
   if(bxShownRole!=roleFilter||bxShownPack!=packFilter||bxShownTool!=buildTool||bxShownPiece!=selectedPiece||bxShownFlag!=flagColor)BxRefreshPalette();
   if(buildVersion!=bxMiniVersion||hoverCell){bxMiniVersion=buildVersion;bxMiniOkBox.MarkDirtyRepaint();}
   var lost=builder.Unreachable();
   bxMiniOk.text=lost==null?"All flags reachable":"A flag is unreachable";bxMiniOk.parent.EnableInClassList("bad",lost!=null);bxOkIcon.Kind=lost==null?"check":"warn";bxOkIcon.Tint=lost==null?new Color(.5f,.85f,.67f):new Color(1,.48f,.48f);
   bxYaw.parent.style.display=buildTool==BuildTool.Piece?DisplayStyle.Flex:DisplayStyle.None;bxYaw.text=buildYaw+"°";bxYawIcon.style.rotate=new StyleRotate(new Rotate(new Angle(buildYaw,AngleUnit.Degree)));
   bxDraft.EnableInClassList("on",bxDirtyNow);bxDraftText.text=bxDirtyNow?"Draft · "+Mathf.Max(1,bxChanges)+(bxChanges>1?" changes":" change"):"Matches the world";
   bxApply.EnableInClassList("off",!bxDirtyNow);bxApply.EnableInClassList("primary",bxDirtyNow);
   if(buildStatus!=bxShownStatus){
    bxShownStatus=buildStatus;
    if(!string.IsNullOrEmpty(buildStatus)){bxToastText.text=buildStatus;bxToast.EnableInClassList("bad",buildProblem);bxToast.AddToClassList("show");bxToastUntil=Time.unscaledTime+(buildProblem?5f:3f);}
   }
   if(bxToast.ClassListContains("show")&&Time.unscaledTime>bxToastUntil)bxToast.RemoveFromClassList("show");
  }
 }

 // Stroke icons drawn with Painter2D on a 24 x 24 grid, so they stay sharp at any size and take a tint.
 public sealed class BxIcon:VisualElement {
  static readonly Dictionary<string,Vector2[][]> Shapes=Build();
  string kind;Color tint=Color.white;
  public string Kind{get=>kind;set{if(kind==value)return;kind=value;MarkDirtyRepaint();}}
  public Color Tint{get=>tint;set{if(tint==value)return;tint=value;MarkDirtyRepaint();}}
  public BxIcon(string kind){this.kind=kind;generateVisualContent+=Draw;}
  static Vector2[] P(params double[] v){var a=new Vector2[v.Length/2];for(int i=0;i<a.Length;i++)a[i]=new Vector2((float)v[i*2],(float)v[i*2+1]);return a;}
  static Vector2[] Arc(double cx,double cy,double r,double from,double to,int n=24){var a=new Vector2[n+1];for(int i=0;i<=n;i++){double t=(from+(to-from)*i/n)*Math.PI/180;a[i]=new Vector2((float)(cx+Math.Cos(t)*r),(float)(cy+Math.Sin(t)*r));}return a;}
  static Vector2[] Flip(Vector2[] v)=>v.Select(p=>new Vector2(24-p.x,p.y)).ToArray();
  static Dictionary<string,Vector2[][]> Build(){
   var undo=new[]{P(9,14,4,9,9,4),P(4,9,14,9),Arc(14,15,6,-90,90,10)};
   return new Dictionary<string,Vector2[][]>{
    {"brush",new[]{P(4,20,5.5,15,16,4.5,19.5,8,9,18.5,4,20),P(14,6.5,17.5,10)}},
    {"pin",new[]{P(12,21,7,14,5.5,10,7,6,12,3.5,17,6,18.5,10,17,14,12,21),Arc(12,10,2.4f,0,360,12)}},
    {"flag",new[]{P(6,21,6,4),P(6,5,17,5,14.5,8.5,17,12,6,12)}},
    {"eraser",new[]{P(4,20,20,20),P(4.5,15,13,6.5,17.5,11,10.5,18,7.5,18,4.5,15)}},
    {"undo",undo},{"redo",undo.Select(Flip).ToArray()},
    {"rotate",new[]{Arc(12,12,8,-60,240),P(19,3.5,19,9,13.5,9)}},
    {"chat",new[]{P(4,5,20,5,20,16,9,16,4,20,4,5)}},
    {"cam",new[]{Arc(12,12,3.2,0,360,16),P(12,3,12,6),P(12,18,12,21),P(3,12,6,12),P(18,12,21,12)}},
    {"menu",new[]{P(5,7,19,7),P(5,12,19,12),P(5,17,19,17)}},
    {"mind",new[]{Arc(12,9.5,6,150,390,24),P(9,15.5,9,17,15,17,15,15.5),P(9.5,20.5,14.5,20.5)}},
    {"self",new[]{Arc(12,8,3.6,0,360,16),P(5,20,6,16,9,14,15,14,18,16,19,20)}},
    {"log",new[]{P(8,6,20,6),P(8,12,20,12),P(8,18,20,18),P(4,6,4.1,6),P(4,12,4.1,12),P(4,18,4.1,18)}},
    {"debug",new[]{P(8,8,4,12,8,16),P(16,8,20,12,16,16),P(13.5,6,10.5,18)}},
    {"play",new[]{P(7,5,19,12,7,19,7,5)}},
    {"stop",new[]{P(6,6,18,6,18,18,6,18,6,6)}},
    {"arrow",new[]{P(5,12,19,12),P(13,6,19,12,13,18)}},
    {"close",new[]{P(6,6,18,18),P(18,6,6,18)}},
    {"shield",new[]{P(12,3,19,6,19,11,15.5,18,12,21,8.5,18,5,11,5,6,12,3)}},
    {"check",new[]{P(5,12.5,9.5,17,19,7.5)}},
    {"warn",new[]{P(12,3.5,21,19.5,3,19.5,12,3.5),P(12,9.5,12,14),P(12,16.5,12,17)}}};
  }
  void Draw(MeshGenerationContext ctx){
   if(kind==null||!Shapes.TryGetValue(kind,out var lines))return;
   var p=ctx.painter2D;float s=Mathf.Min(contentRect.width,contentRect.height)/24f;if(s<=0)return;
   p.strokeColor=tint;p.lineWidth=Mathf.Max(1.4f,1.9f*s);p.lineCap=LineCap.Round;p.lineJoin=LineJoin.Round;
   foreach(var l in lines){p.BeginPath();p.MoveTo(l[0]*s);for(int i=1;i<l.Length;i++)p.LineTo(l[i]*s);if(kind=="play"){p.ClosePath();p.fillColor=tint;p.Fill();}p.Stroke();}
  }
 }
}
