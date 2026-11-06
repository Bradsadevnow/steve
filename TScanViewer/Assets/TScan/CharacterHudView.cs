using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;
using MoonTribe.UI;

namespace Steve.TScan {
 // Human-facing view only: observations in, inspect/edit navigation out. No action execution.
 public sealed class CharacterHudView:IDisposable {
  public VisualElement Root {get;}
  public VisualElement ChatAnchor {get;}
  public VisualElement TransportAnchor {get;}
  public bool Expanded {get;private set;}
  readonly CharacterPresentation model=new CharacterPresentation();
  readonly CharacterPortrait portrait=new CharacterPortrait();
  readonly VisualElement art,portraitImage,modules,popup;
  readonly Label name,status,position,stamp,details;
  readonly Button expand;
  readonly ScrollView sheet;
  readonly Dictionary<string,Label> attributes=new Dictionary<string,Label>();
  readonly Dictionary<string,ResourceBar> bars=new Dictionary<string,ResourceBar>();
  string equipmentKey="",sheetKey="",selected="";
  sealed class ResourceBar {public HealthBarElement bar;public VisualElement host;public Label label;public float current=-1,maximum=-1;}
  static VisualElement El(VisualElement parent,string css){var e=new VisualElement();foreach(var name in css.Split(' '))e.AddToClassList(name);parent.Add(e);return e;}
  static Label Text(VisualElement parent,string value,string css){var l=new Label(value);l.AddToClassList(css);parent.Add(l);return l;}
  static void IgnoreTree(VisualElement root){root.pickingMode=PickingMode.Ignore;foreach(var child in root.Children())IgnoreTree(child);}
  static void Rect(VisualElement e,float x,float y,float width,float height){e.style.position=Position.Absolute;e.style.left=x;e.style.top=y;e.style.width=width;e.style.height=height;}
  public CharacterHudView(VisualElement parent,Action edit){
   Root=El(parent,"character-hud");Root.name="character-hud";
   var fit=new PaintedFrame{DesignWidth=360,DesignHeight=190,MaxScale=1};Rect(fit,0,0,360,190);Root.Add(fit);
   art=El(fit,"hud-art");
   portraitImage=El(art,"hud-portrait");Rect(portraitImage,15,14,46,46);portraitImage.tooltip="Confirmed body and equipment";
   name=Text(art,"Steve · Lv —","hud-name");Rect(name,72,13,196,24);
   status=Text(art,"Waiting","hud-status");Rect(status,72,38,160,20);
   expand=new Button(()=>SetExpanded(!Expanded)){text="Sheet +",name="character-sheet-toggle"};expand.AddToClassList("hud-toggle");Rect(expand,274,17,70,30);art.Add(expand);
   TransportAnchor=El(art,"hud-transport");Rect(TransportAnchor,240,48,62,20);
   ChatAnchor=El(art,"hud-chat-anchor");Rect(ChatAnchor,314,48,30,20);
   MakeBar("HP","UI/CharacterHud/health",70);MakeBar("MP","UI/CharacterHud/mana",96);
   var row=El(art,"hud-attributes");Rect(row,15,126,330,24);
   foreach(var id in CharacterPresentation.Attributes){var label=Text(row,id+" —","hud-attribute");attributes[id]=label;}
   modules=El(art,"hud-modules");Rect(modules,14,151,205,28);
   position=Text(art,"Position unavailable","hud-position");Rect(position,223,154,122,23);
   popup=El(Root,"hud-sheet");popup.name="character-sheet-expanded";popup.style.display=DisplayStyle.None;
   var header=El(popup,"hud-sheet-header");Text(header,"CHARACTER SHEET","hud-sheet-title");
   var close=new Button(()=>SetExpanded(false)){text="Close",name="character-sheet-close"};close.AddToClassList("hud-toggle");header.Add(close);
   stamp=Text(popup,"Waiting for confirmed state","hud-muted");
   sheet=new ScrollView(ScrollViewMode.Vertical){horizontalScrollerVisibility=ScrollerVisibility.Hidden};sheet.AddToClassList("hud-sheet-scroll");popup.Add(sheet);
   details=Text(popup,"","hud-module-detail");details.style.display=DisplayStyle.None;
   var editButton=new Button(()=>{SetExpanded(false);edit();}){text="Edit loadout",name="hud-edit-loadout"};editButton.AddToClassList("hud-edit");popup.Add(editButton);
  }
  void MakeBar(string id,string resource,float y){
   var host=El(art,"hud-resource");Rect(host,15,y,330,24);
   var visual=El(host,"hud-resource-art");Rect(visual,0,-4,330,33);
   var template=Resources.Load<VisualTreeAsset>(resource);HealthBarElement control=null;
   if(template!=null){var tree=template.Instantiate();tree.style.flexGrow=1;visual.Add(tree);control=tree.Q<HealthBarElement>();IgnoreTree(tree);}
   var label=Text(host,id+" — / —","hud-resource-label");Rect(label,0,0,330,24);label.pickingMode=PickingMode.Ignore;
   bars[id]=new ResourceBar{bar=control,host=host,label=label};
  }
  public event Action<bool> ExpansionChanged;
  public void SetExpanded(bool value){bool changed=Expanded!=value;Expanded=value;popup.style.display=value?DisplayStyle.Flex:DisplayStyle.None;expand.text=value?"Sheet −":"Sheet +";sheetKey="";if(changed)ExpansionChanged?.Invoke(value);}
  void BindResource(string id,CharacterResourceView value){
   var item=bars[id];bool valid=CharacterPresentation.Valid(value);
   item.host.EnableInClassList("unavailable",!valid);item.host.tooltip=valid?(model.Fresh?"Confirmed ":"Last confirmed ")+id:"Waiting for a confirmed "+id+" value";
   item.label.text=id+" "+(valid?CharacterPresentation.Number(value.current)+" / "+CharacterPresentation.Number(value.maximum):"— / —");
   if(item.bar==null)return;
   var max=valid?value.maximum:1;var current=valid?value.current:0;
   if(item.maximum!=max||item.current!=current){item.bar.SetMax(max);item.bar.SetValue(current,instant:item.maximum<0||!valid);item.maximum=max;item.current=current;}
  }
  public void Update(GridSnapshot snapshot,bool ready,string state,Transform portraitOwner,bool visible){
   model.Update(snapshot,ready,state);
   Root.EnableInClassList("stale",!model.Fresh);Root.tooltip=model.Fresh?"Confirmed character · "+model.Observation:"Last confirmed state · waiting for a fresh observation";
   name.text="Steve · Lv "+(model.Sheet?.level>0?model.Sheet.level.ToString():"—");
   status.text=!model.Fresh?"Stale · "+state:state+" · "+(CharacterCatalog.Body(model.Character.body_id)?.name??model.Character.body_id);
   position.text=model.Position;
   foreach(var id in CharacterPresentation.Attributes){var stat=model.Attribute(id);attributes[id].text=id+" "+(stat==null?"—":CharacterPresentation.Number(stat.effective));}
   BindResource("HP",model.Sheet?.hp);BindResource("MP",model.Sheet?.mp);
   if(portraitOwner){portrait.Update(model.Character,portraitOwner,visible);if(portrait.Texture)portraitImage.style.backgroundImage=new StyleBackground(Background.FromRenderTexture(portrait.Texture));}
   var key=model.Character==null?"":JsonUtility.ToJson(model.Character);var visualKey=CharacterCatalog.VisualKey(model.Character);
   if(visualKey!=equipmentKey){equipmentKey=visualKey;BuildModules();sheetKey="";}
   if(Expanded){
    stamp.text=(model.Fresh?"Confirmed":"Stale · last confirmed")+" · loadout r"+(model.Character?.revision.ToString()??"—");
    if(key!=sheetKey){sheetKey=key;BuildSheet();}
   }
   var width=parentWidth();bool compact=width<1300;Root.style.width=compact?320:360;Root.style.height=compact?169:190;
   fitSize(compact?320:360,compact?169:190);
   popup.style.maxHeight=Mathf.Min(480,Mathf.Max(180,(Root.panel?.visualTree.layout.height??900)-(compact?169:190)-32));
  }
  float parentWidth()=>Root.parent?.resolvedStyle.width??1600;
  void fitSize(float width,float height){var fit=Root[0];fit.style.width=width;fit.style.height=height;popup.style.top=height+8;}
  void BuildModules(){
   modules.Clear();var equipment=model.Character?.equipment??Array.Empty<CharacterEquipment>();
   foreach(var item in equipment.Take(5)){
    var captured=item;var button=new Button(()=>{selected=captured.module_id;SetExpanded(true);ShowDetails();}){tooltip=CharacterPresentation.ModuleName(item.module_id)+" · "+CharacterPresentation.Name(item.socket_id)+" · generic icon",name="hud-module-"+item.socket_id};button.AddToClassList("hud-module");
    var icon=El(button,"hud-module-icon");icon.style.backgroundImage=new StyleBackground(CharacterPresentation.ModuleIcon(item.module_id));icon.pickingMode=PickingMode.Ignore;modules.Add(button);
   }
   if(equipment.Length>5){var more=new Button(()=>SetExpanded(true)){text="+"+(equipment.Length-5)};more.AddToClassList("hud-toggle");modules.Add(more);}
   if(equipment.Length==0)Text(modules,"No modules equipped","hud-muted");
  }
  void Heading(string text)=>Text(sheet.contentContainer,text,"hud-section-title");
  void BuildSheet(){
   sheet.Clear();Heading("ATTRIBUTES");
   var headings=El(sheet.contentContainer,"hud-stat-row hud-stat-columns");
   Text(headings,"Stat","hud-stat-id");foreach(var heading in new[]{"Base","Level","Gear","Temp","Total"})Text(headings,heading,"hud-stat-value");
   foreach(var id in CharacterPresentation.Attributes){
    var a=model.Attribute(id);var values=a==null?new[]{"—","—","—","—","—"}:new[]{CharacterPresentation.Number(a.base_value),CharacterPresentation.Number(a.level_bonus),CharacterPresentation.Number(a.equipment_bonus),CharacterPresentation.Number(a.temporary_bonus),CharacterPresentation.Number(a.effective)};
    var row=El(sheet.contentContainer,"hud-stat-row");Text(row,id,"hud-stat-id");foreach(var value in values)Text(row,value,"hud-stat-value");
   }
   if(model.Sheet==null)Text(sheet.contentContainer,"Character stats are not available yet.","hud-muted");
   Heading("MOUNTS / EQUIPMENT");var body=CharacterCatalog.Body(model.Character?.body_id);var equipment=model.Character?.equipment??Array.Empty<CharacterEquipment>();
   foreach(var socket in body?.sockets??Array.Empty<CharacterSocket>()){
    var item=equipment.FirstOrDefault(e=>e.socket_id==socket.id);
    var reserved=equipment.FirstOrDefault(e=>CharacterCatalog.Module(e.module_id)?.slots==2&&(body.pairs??Array.Empty<CharacterPair>()).Any(p=>p.primary==e.socket_id&&p.secondary==socket.id));
    var text=CharacterPresentation.Name(socket.id)+" · "+(item!=null?CharacterPresentation.ModuleName(item.module_id):reserved!=null?"Reserved · "+CharacterPresentation.ModuleName(reserved.module_id):"Empty");
    if(item==null)Text(sheet.contentContainer,text,"hud-mount-empty");
    else{var id=item.module_id;var button=new Button(()=>{selected=id;ShowDetails();}){text=text};button.AddToClassList("hud-mount");sheet.Add(button);}
   }
   if(body?.sockets?.Length==0)Text(sheet.contentContainer,"This body has no equipment mounts.","hud-muted");
   Heading("AVAILABLE ABILITIES");var actions=model.Character?.capabilities??Array.Empty<string>();
   foreach(var action in actions){
    var evaluated=model.Sheet?.abilities?.FirstOrDefault(a=>a.id==action);
    if(evaluated!=null){Text(sheet.contentContainer,evaluated.name+" · "+evaluated.damage+" damage","hud-ability-name");Text(sheet.contentContainer,evaluated.stat+" "+evaluated.effective_stat+" · "+evaluated.description,"hud-ability-description");continue;}
    var module=equipment.Select(e=>CharacterCatalog.Module(e.module_id)).FirstOrDefault(m=>m!=null&&(m.actions??Array.Empty<string>()).Contains(action));
    Text(sheet.contentContainer,CharacterPresentation.Name(action),"hud-ability-name");
    if(module!=null)Text(sheet.contentContainer,module.description,"hud-ability-description");
   }
   if(actions.Length==0)Text(sheet.contentContainer,"No equipped combat abilities.","hud-muted");
   ShowDetails();
  }
  void ShowDetails(){
   var equipped=(model.Character?.equipment??Array.Empty<CharacterEquipment>()).Any(e=>e.module_id==selected);var module=equipped?CharacterCatalog.Module(selected):null;
   details.style.display=module==null?DisplayStyle.None:DisplayStyle.Flex;
   if(module!=null){details.text=module.name+"\n"+module.description;foreach(var ability in model.Sheet?.abilities??Array.Empty<CharacterAbilityView>())if((module.actions??Array.Empty<string>()).Contains(ability.id))details.text+="\nCurrent damage: "+ability.damage;}
  }
  public void Dispose()=>portrait.Dispose();
 }
}
