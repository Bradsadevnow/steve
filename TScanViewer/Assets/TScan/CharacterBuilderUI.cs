using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UIElements;

namespace Steve.TScan {
 public sealed partial class TScanViewer {
  [SerializeField,HideInInspector] bool characterOpen;
  bool characterApplying;
  [SerializeField,HideInInspector] CharacterState characterDraft;
  CharacterState characterConfirmed;
  bool CharacterBuilderVisible=>characterOpen&&buildOpen&&!cinema&&!memoryFlyout;
  string characterSocket="",characterMessage="",characterKey="";string characterRequestId="",characterRequestJson="";
  CharacterState characterStatsPreview;string characterPreviewKey="",characterPreviewError="";
  VisualElement characterPanel,characterBodies,characterSlots,characterModules,characterBuildStats,characterBuildAbilities;Label characterDetails,characterNotice,characterComparison,characterBuildResources,characterBuildStamp;Foldout characterChassis;
  RenderTexture characterTexture;Camera characterCamera;GameObject characterStage,characterPreview;float characterYaw=25;float characterZoom=1,characterFit=1.7f;Vector2 characterPointer;bool characterRotating;
  void SetCharacterOpen(bool value){characterOpen=value;if(value){EnsureCharacterDraft();RefreshCharacter();}else DestroyCharacterStage();}
  void EnsureCharacterDraft(){
   var state=DashboardBody?.Bench?.State?.character;
   if(state!=null&&state.catalog_version==CharacterCatalog.Data.version){if(characterConfirmed==null||state.revision>=characterConfirmed.revision)characterConfirmed=CharacterCatalog.Copy(state);}else state=null;
   if(characterDraft==null)characterDraft=CharacterCatalog.Copy(state??new CharacterState{catalog_version=CharacterCatalog.Data.version});
   if(characterDraft.catalog_version=="steve-equipment-v1"&&CharacterCatalog.Data.version=="steve-equipment-v2"){
    characterDraft.catalog_version=CharacterCatalog.Data.version;characterDraft.sheet=null;characterMessage="Equipment rules updated: sword +2 STR, shield +2 CON. Review the draft before Apply.";
   }
  }
  void BuildCharacterPanel(){
   characterPanel=BxEl("character-panel glass",bxRoot);characterPanel.name="character-builder";characterPanel.style.display=DisplayStyle.None;
   BuildEquipmentSheet(characterPanel);
   var sidebar=BxEl("character-sidebar glass",characterPanel);sidebar.name="character-build-controls";
   var controls=new ScrollView(ScrollViewMode.Vertical){horizontalScrollerVisibility=ScrollerVisibility.Hidden};controls.AddToClassList("character-controls-scroll");sidebar.Add(controls);
   var body=controls.contentContainer;
   BxLabel("BUILD SHEET","character-title",body);
   characterChassis=new Foldout{text="Chassis",value=false};characterChassis.AddToClassList("character-chassis-choice");body.Add(characterChassis);
   characterBodies=BxEl("character-bodies",characterChassis);
   characterDetails=BxLabel("","character-details",body);characterNotice=BxLabel("","character-notice",body);
   characterBuildStamp=BxLabel("Waiting for engine preview","build-sheet-stamp",body);
   characterBuildResources=BxLabel("","build-sheet-resources",body);
   BxLabel("ATTRIBUTES","label-cap",body);characterBuildStats=BxEl("build-sheet-stats",body);characterBuildStats.name="build-sheet-stats";
   BxLabel("GRANTED ABILITIES","label-cap",body);characterBuildAbilities=BxEl("build-sheet-abilities",body);characterBuildAbilities.name="build-sheet-abilities";
   var comparison=new Foldout{text="Changes from equipped",value=false,name="character-draft-comparison"};comparison.AddToClassList("character-comparison");body.Add(comparison);
   var comparisonScroll=new ScrollView(ScrollViewMode.Vertical);comparisonScroll.style.maxHeight=100;comparison.Add(comparisonScroll);
   characterComparison=BxLabel("","character-comparison-text",comparisonScroll.contentContainer);
   var cameraControls=BxEl("character-camera-controls",body);
   BxButton("−","btn ghost",()=>ZoomCharacter(1.2f),cameraControls);
   BxButton("Reset view","btn ghost",()=>{characterYaw=25;characterZoom=1;if(characterPreview)characterPreview.transform.localRotation=Quaternion.Euler(0,characterYaw,0);FitCharacterPreview();},cameraControls);
   BxButton("+","btn ghost",()=>ZoomCharacter(1/1.2f),cameraControls);
   var footer=BxEl("character-footer",body);
   BxButton("Starter pair","btn ghost",()=>{characterDraft.body_id="unicore";characterDraft.equipment=new[]{new CharacterEquipment{socket_id="arm_R",module_id="warrior_blade"},new CharacterEquipment{socket_id="arm_L",module_id="warrior_shield"}};characterSocket="arm_R";CharacterEdited();},footer);
   BxButton("Revert","btn ghost",()=>{if(characterConfirmed!=null){characterDraft=CharacterCatalog.Copy(characterConfirmed);characterRequestId="";characterRequestJson="";characterMessage="Reverted to confirmed equipment.";RefreshCharacter();}},footer);
   BxButton("Apply loadout","btn primary character-apply",()=>{if(!characterApplying)StartCoroutine(ApplyCharacter());},sidebar).name="character-apply";
   BuildModuleTooltip();
  }
  void CharacterEdited(){characterRequestId="";characterRequestJson="";characterMessage="Draft — not applied";RefreshCharacter();}
  void EquipmentTile(Button button,CharacterModule module){
   var caption=button.ClassListContains("module-button")?module?.name:button.text.Replace('_',' ');button.text="";button.AddToClassList("equipment-tile");
   if(module!=null){var icon=BxEl("equipment-icon",button);icon.pickingMode=PickingMode.Ignore;icon.style.backgroundImage=new StyleBackground(CharacterPresentation.ModuleIcon(module.id));}
   BxLabel(caption,"equipment-name",button);
   if(module!=null){button.RegisterCallback<PointerEnterEvent>(_=>ShowModuleTooltip(module,button));button.RegisterCallback<PointerLeaveEvent>(_=>HideModuleTooltip());button.RegisterCallback<DetachFromPanelEvent>(_=>HideModuleTooltip());}
  }
  void RefreshCharacter(){
   if(characterPanel==null)return;HideModuleTooltip();EnsureCharacterDraft();var draft=characterDraft;characterBodies.Clear();
   foreach(var body in CharacterCatalog.Data.bodies){var id=body.id;var button=BxButton(body.name,"btn ghost",()=>{draft.body_id=id;characterSocket="";CharacterEdited();},characterBodies);button.EnableInClassList("on",draft.body_id==id);}
   var selectedBody=CharacterCatalog.Body(draft.body_id);characterSlots.Clear();

   foreach(var slot in selectedBody.sockets){
    var id=slot.id;var item=draft.equipment.FirstOrDefault(e=>e.socket_id==id);var pair=draft.equipment.FirstOrDefault(e=>CharacterCatalog.Module(e.module_id)?.slots==2&&selectedBody.pairs.Any(p=>p.primary==e.socket_id&&p.secondary==id));
    var label=id.Replace('_',' ')+"\n"+(item!=null?CharacterCatalog.Module(item.module_id)?.name:pair!=null?"Reserved by "+pair.module_id:"Empty · "+slot.type);
    var button=BxButton(label,"btn ghost mount-button",()=>{characterSocket=id;RefreshCharacter();},characterSlots);EquipmentTile(button,item!=null?CharacterCatalog.Module(item.module_id):null);PositionSheetSlot(button,Array.IndexOf(selectedBody.sockets,slot));button.EnableInClassList("on",characterSocket==id);
   }
   var unresolved=draft.equipment.Where(e=>!selectedBody.sockets.Any(s=>s.id==e.socket_id)).ToArray();
   foreach(var item in unresolved){var captured=item;BxButton("Remove unresolved: "+item.socket_id+" / "+item.module_id,"btn ghost mount-button",()=>{draft.equipment=draft.equipment.Where(e=>e!=captured).ToArray();CharacterEdited();},characterSlots);}
   characterModules.Clear();var active=selectedBody.sockets.FirstOrDefault(s=>s.id==characterSocket);
   var moduleHeader=BxEl("character-module-header",characterModules);
   BxLabel(active==null?"SELECT A MOUNT":"MODULES / "+active.type.ToUpperInvariant(),"label-cap",moduleHeader);
   if(active!=null){
    BxButton("Unequip","btn ghost character-unequip",()=>{draft.equipment=draft.equipment.Where(e=>e.socket_id!=active.id).ToArray();CharacterEdited();},moduleHeader).tooltip="Unequip this mount";
    foreach(var mod in CharacterCatalog.Data.modules.Where(m=>m.mount_types.Contains(active.type))){var id=mod.id;var button=BxButton(mod.name,"btn ghost module-button",()=>{
     var proposed=CharacterCatalog.Copy(draft);proposed.equipment=proposed.equipment.Where(e=>e.socket_id!=active.id).Concat(new[]{new CharacterEquipment{socket_id=active.id,module_id=id}}).ToArray();var error=CharacterCatalog.Validate(proposed);
     if(error!=null){characterMessage=error;characterNotice.text=error;return;}draft.equipment=proposed.equipment;CharacterEdited();
    },characterModules);button.name="equip-"+id;EquipmentTile(button,mod);}
   }
   var validation=CharacterCatalog.Validate(draft);
   characterChassis.text="Chassis · "+selectedBody.name;
   characterDetails.text=draft.equipment.Length+" modules equipped";
   characterNotice.text=validation??characterMessage;
   QueueCharacterStatsPreview();
   characterPanel.Q<Button>("character-apply").SetEnabled(!characterApplying&&validation==null&&characterConfirmed!=null);
   RebuildCharacterPreview();
  }
  void QueueCharacterStatsPreview(){
   if(characterConfirmed==null||characterConfirmed.catalog_version!=CharacterCatalog.Data.version||CharacterCatalog.Validate(characterDraft)!=null){characterStatsPreview=null;characterPreviewKey="";UpdateCharacterComparison();return;}
   var request=new CharacterPreviewRequest{expected_revision=characterConfirmed.revision,catalog_version=characterDraft.catalog_version,body_id=characterDraft.body_id,equipment=characterDraft.equipment};
   var key=JsonUtility.ToJson(request);
   if(key!=characterPreviewKey){characterPreviewKey=key;characterStatsPreview=null;characterPreviewError="";StartCoroutine(PreviewCharacterStats(key));}
   UpdateCharacterComparison();
  }
  void UpdateCharacterComparison(){if(characterComparison!=null)characterComparison.text=CharacterPresentation.DraftComparison(characterConfirmed,characterDraft,characterStatsPreview)+(string.IsNullOrEmpty(characterPreviewError)?"":"\n"+characterPreviewError);UpdateCharacterBuildSheet();}
  void UpdateCharacterBuildSheet(){
   if(characterBuildStats==null)return;
   characterBuildStats.Clear();characterBuildAbilities.Clear();
   var sheet=characterStatsPreview?.sheet;
   characterBuildStamp.text=sheet!=null?"ENGINE PREVIEW · NOT APPLIED":!string.IsNullOrEmpty(characterPreviewError)?"Engine preview unavailable":"Waiting for engine preview";
   characterBuildStamp.tooltip=characterPreviewError;
   System.Func<CharacterResourceView,string> resource=r=>CharacterPresentation.Valid(r)?CharacterPresentation.Number(r.current)+" / "+CharacterPresentation.Number(r.maximum):"— / —";
   characterBuildResources.text="Level "+(sheet!=null?sheet.level.ToString():"—")+"\nHP "+resource(sheet?.hp)+"    MP "+resource(sheet?.mp);
   characterBuildResources.tooltip="Max HP: 10 base + 1 per CON above 1. Equipment changes do not heal.";
   foreach(var id in CharacterPresentation.Attributes){
    var stat=sheet?.attributes?.FirstOrDefault(a=>string.Equals(a.id,id,StringComparison.OrdinalIgnoreCase));
    var current=characterConfirmed?.sheet?.attributes?.FirstOrDefault(a=>string.Equals(a.id,id,StringComparison.OrdinalIgnoreCase));
    var row=BxEl("build-stat-row",characterBuildStats);row.name="build-stat-"+id;BxLabel(id,"build-stat-id",row);
    BxLabel(stat==null?"—":CharacterPresentation.Number(stat.effective),"build-stat-total",row);
    float delta=stat!=null&&current!=null?stat.effective-current.effective:0;
    var change=BxLabel(delta==0?"":(delta>0?"+":"")+CharacterPresentation.Number(delta),"build-stat-delta",row);change.EnableInClassList("loss",delta<0);change.tooltip="Change from equipped loadout";
    if(stat!=null)row.tooltip="Base "+CharacterPresentation.Number(stat.base_value)+" · Level "+CharacterPresentation.Number(stat.level_bonus)+" · Gear "+CharacterPresentation.Number(stat.equipment_bonus)+" · Temporary "+CharacterPresentation.Number(stat.temporary_bonus);
   }
   if(sheet==null){BxLabel("Abilities will appear with the engine preview.","build-ability-detail",characterBuildAbilities);return;}
   foreach(var ability in sheet.abilities??Array.Empty<CharacterAbilityView>()){
    var card=BxEl("build-ability",characterBuildAbilities);card.name="build-ability-"+ability.id;
    BxLabel(ability.name+" · "+ability.damage+" damage","build-ability-name",card);
    BxLabel("Range "+ability.reach+" · Scales with "+ability.stat,"build-ability-detail",card);card.tooltip=ability.description;
   }
   if((sheet.abilities?.Length??0)==0)BxLabel("No equipped combat abilities.","build-ability-detail",characterBuildAbilities);
   int prototypes=characterDraft.equipment.Count(e=>(CharacterCatalog.Module(e.module_id)?.actions?.Length??0)==0);
   if(prototypes>0)BxLabel(prototypes+" visual-only module"+(prototypes==1?"":"s"),"build-ability-detail",characterBuildAbilities);
  }
  IEnumerator PreviewCharacterStats(string key){
   using(var req=new UnityWebRequest(Endpoint+"/character/preview","POST")){
    req.uploadHandler=new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(key));req.downloadHandler=new DownloadHandlerBuffer();req.SetRequestHeader("Content-Type","application/json");req.timeout=5;yield return req.SendWebRequest();
    if(key!=characterPreviewKey)yield break;
    if(req.result==UnityWebRequest.Result.Success){var value=JsonUtility.FromJson<CharacterPreviewReceipt>(req.downloadHandler.text);if(value!=null&&value.preview&&value.expected_revision==characterConfirmed?.revision&&value.character?.sheet?.revision>0)characterStatsPreview=value.character;else characterPreviewError="Preview unavailable; refresh before relying on proposed stats.";}
    else{characterPreviewError="Preview unavailable: "+(string.IsNullOrEmpty(req.downloadHandler.text)?req.error:req.downloadHandler.text);characterPreviewKey="";}
    UpdateCharacterComparison();
   }
  }
  IEnumerator ApplyCharacter(){
   EnsureCharacterDraft();var error=CharacterCatalog.Validate(characterDraft);var grid=DashboardBody?.Bench;
   if(error!=null||characterConfirmed==null||grid==null){characterMessage=error??"Waiting for backend character state.";RefreshCharacter();yield break;}
   if(grid.State.running||grid.Busy||sending){characterMessage="Stop Steve and wait for inference/presentation before Apply.";RefreshCharacter();yield break;}
   characterApplying=true;characterMessage="Awaiting backend confirmation…";RefreshCharacter();
   if(string.IsNullOrEmpty(characterRequestId))characterRequestId=Guid.NewGuid().ToString("N");
   var request=new CharacterApplyRequest{request_id=characterRequestId,expected_revision=characterConfirmed.revision,catalog_version=characterDraft.catalog_version,body_id=characterDraft.body_id,equipment=characterDraft.equipment};
   if(string.IsNullOrEmpty(characterRequestJson))characterRequestJson=JsonUtility.ToJson(request);
   using(var req=new UnityWebRequest(Endpoint+"/character/apply","POST")){
    req.uploadHandler=new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(characterRequestJson));req.downloadHandler=new DownloadHandlerBuffer();req.SetRequestHeader("Content-Type","application/json");req.timeout=8;yield return req.SendWebRequest();
    if(req.result==UnityWebRequest.Result.Success){var receipt=JsonUtility.FromJson<CharacterApplyReceipt>(req.downloadHandler.text);if(receipt?.character!=null&&receipt.outcome=="loadout_applied"){characterConfirmed=receipt.character;characterDraft=CharacterCatalog.Copy(receipt.character);characterMessage="Applied · confirmed revision "+receipt.character.revision;characterRequestId="";characterRequestJson="";}else characterMessage="Unconfirmed response. Refresh before relying on this build.";}
    else characterMessage="Apply not confirmed: "+(string.IsNullOrEmpty(req.downloadHandler.text)?req.error:req.downloadHandler.text)+". Retry uses the same request ID.";
   }
   characterApplying=false;RefreshCharacter();
  }
  void RebuildCharacterPreview(){
   if(!characterStage){
    PreviewStudioLifetime.Reclaim(transform,"Character preview studio");
    characterStage=new GameObject("Character preview studio"){hideFlags=HideFlags.DontSave};characterStage.transform.SetParent(transform,false);characterStage.transform.position=new Vector3(0,-100,0);
    characterTexture=new RenderTexture(650,750,24){name="Character preview",hideFlags=HideFlags.DontSave};
    var cameraGo=new GameObject("Preview camera");cameraGo.transform.SetParent(characterStage.transform,false);characterCamera=cameraGo.AddComponent<Camera>();characterCamera.cullingMask=1<<29;characterCamera.targetTexture=characterTexture;characterCamera.clearFlags=CameraClearFlags.SolidColor;characterCamera.backgroundColor=new Color(.035f,.045f,.055f);characterCamera.nearClipPlane=.1f;characterCamera.farClipPlane=20;characterCamera.orthographic=true;characterCamera.orthographicSize=1.7f;cameraGo.transform.localPosition=new Vector3(0,1.4f,-7);cameraGo.transform.localRotation=Quaternion.identity;
    var lightGo=new GameObject("Preview light");lightGo.transform.SetParent(characterStage.transform,false);lightGo.transform.localRotation=Quaternion.Euler(40,-30,0);var light=lightGo.AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.4f;light.cullingMask=1<<29;
   }
   if(characterPreview){characterPreview.SetActive(false);Destroy(characterPreview);}characterPreview=CharacterCatalog.Create(characterDraft,characterStage.transform,29,true);characterPreview.transform.localRotation=Quaternion.Euler(0,characterYaw,0);
   FitCharacterPreview();
   characterPanel.Q<VisualElement>("character-preview").style.backgroundImage=new StyleBackground(Background.FromRenderTexture(characterTexture));
   ResizeCharacterPreview(characterPanel.Q<VisualElement>("character-preview"));
  }
  void DestroyCharacterStage(){PreviewStudioLifetime.Release(characterStage);characterStage=null;characterTexture=null;characterPreview=null;characterCamera=null;}
  void UpdateCharacterUI(){
   if(!CharacterBuilderVisible)HideModuleTooltip();else moduleInspectPreview?.Tick();
   var state=DashboardBody?.Bench?.State?.character;if(state!=null&&state.catalog_version==CharacterCatalog.Data.version&&(characterConfirmed==null||state.revision>=characterConfirmed.revision))characterConfirmed=CharacterCatalog.Copy(state);
   if(characterPanel==null)return;
   bool show=CharacterBuilderVisible;characterPanel.style.display=show?DisplayStyle.Flex:DisplayStyle.None;
   if(show){EnsureCharacterDraft();if(!characterStage)RebuildCharacterPreview();var key=characterConfirmed==null?"offline":characterConfirmed.revision.ToString();if(characterKey!=key){characterKey=key;RefreshCharacter();}}
   else if(characterStage)DestroyCharacterStage();
  }
 }
}
