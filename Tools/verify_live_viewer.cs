// UI-only runtime smoke check. Preserves the operator's draft and restores the current workspace.
var viewer=UnityEngine.Object.FindAnyObjectByType<Steve.TScan.TScanViewer>();
var flags=System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic;var type=viewer.GetType();
System.Func<string,object> field=name=>type.GetField(name,flags).GetValue(viewer);
System.Action<string,object[]> invoke=(name,args)=>type.GetMethod(name,flags).Invoke(viewer,args);
System.Func<string,UnityEngine.UIElements.VisualElement> el=name=>(UnityEngine.UIElements.VisualElement)field(name);
var originalBuild=(bool)field("buildOpen");var originalCharacter=(bool)field("characterOpen");var originalTab=(string)field("shTab");
var originalCinema=(bool)field("cinema");var originalMemory=(bool)field("memoryFlyout");
var originalDraft=UnityEngine.JsonUtility.ToJson(field("characterDraft"));var originalWorldDraft=(string)field("buildDraftReload");
var report=new System.Collections.Generic.Dictionary<string,object>();
System.Collections.IEnumerator VerifySteps(){
  type.GetField("cinema",flags).SetValue(viewer,false);type.GetField("memoryFlyout",flags).SetValue(viewer,false);
  invoke("ShSetMode",new object[]{false});type.GetField("shTab",flags).SetValue(viewer,"mind");
  yield return null;yield return null;yield return null;
  var root=el("shRoot");var pane=el("shPane");var map=UnityEngine.UIElements.UQueryExtensions.Q<UnityEngine.UIElements.VisualElement>(root,"watch-world-minimap");
  if(UnityEngine.UIElements.UQueryExtensions.Q<UnityEngine.UIElements.VisualElement>(root,"watch-goals")!=null)throw new System.Exception("Duplicate Goals panel remains");
  if(map.worldBound.yMin>root.worldBound.yMin+32||pane.worldBound.yMin<map.worldBound.yMax||!pane.Contains(el("shTools"))||!pane.Contains(el("shRail")))throw new System.Exception("Watch controls/map/flyout placement incorrect");
  invoke("UpdateShell",null);
  if(el("shCard").style.display.value==UnityEngine.UIElements.DisplayStyle.None)throw new System.Exception("Watch HUD missing; build="+field("buildOpen")+", cinema="+field("cinema")+", memory="+field("memoryFlyout"));
  report["watch_map_toolbar_existing_goals_flyout"]=true;
  invoke("ShSetMode",new object[]{true});invoke("SetCharacterOpen",new object[]{false});
  yield return null;yield return null;yield return null;
  var options=el("bxOptions");var assets=el("bxStack");var builderRoot=el("bxRoot");var inspector=UnityEngine.UIElements.UQueryExtensions.Q<UnityEngine.UIElements.VisualElement>(builderRoot,"builder-selection-inspector");
  if(el("shCard").resolvedStyle.display!=UnityEngine.UIElements.DisplayStyle.None||options.worldBound.yMax>inspector.worldBound.yMin||assets.worldBound.yMax>inspector.worldBound.yMin)throw new System.Exception("Builder panel overlap or HUD visible");
  var point=new UnityEngine.Vector2((options.worldBound.xMax+assets.worldBound.xMin)*.5f,(options.worldBound.yMin+options.worldBound.yMax)*.5f);
  if(builderRoot.panel.Pick(point)!=null)throw new System.Exception("Center placement area blocked by UI");
  report["world_builder_inspector_clear_input"]=true;
  invoke("SetCharacterOpen",new object[]{true});yield return null;yield return null;yield return null;
  invoke("RefreshCharacter",null);invoke("RefreshCharacter",null);yield return null;yield return null;
  int studios=0;foreach(var camera in UnityEngine.Object.FindObjectsByType<UnityEngine.Camera>())if(camera.enabled&&camera.transform.parent.name=="Character preview studio")studios++;
  if(studios!=1)throw new System.Exception("Character preview studio count: "+studios);
  var mesh=Steve.TScan.CharacterCatalog.Mesh("module_warrior_blade");if(Steve.TScan.CharacterCatalog.Mesh("nonexistent_qa_asset")!=null||!mesh)throw new System.Exception("Missing mesh lookup invalidated existing meshes");
  var draft=(Steve.TScan.CharacterState)field("characterDraft");var visualKey=Steve.TScan.CharacterCatalog.VisualKey(draft);var altered=Steve.TScan.CharacterCatalog.Copy(draft);altered.sheet=null;if(Steve.TScan.CharacterCatalog.VisualKey(altered)!=visualKey)throw new System.Exception("Visual key depends on stats");
  var panel=el("characterPanel");var anchor=UnityEngine.UIElements.UQueryExtensions.Q<UnityEngine.UIElements.VisualElement>(panel,"character-preview");invoke("ShowModuleTooltip",new object[]{Steve.TScan.CharacterCatalog.Module("warrior_shield"),anchor});
  var preview=(Steve.TScan.ModuleInspectPreview)field("moduleInspectPreview");var pivot=(UnityEngine.GameObject)typeof(Steve.TScan.ModuleInspectPreview).GetField("pivot",flags).GetValue(preview);var turntable=pivot.transform;var studio=turntable.parent;var before=turntable.localRotation;
  for(int i=0;i<3;i++)preview.Tick();
  if(UnityEngine.Quaternion.Angle(before,turntable.localRotation)<.1f)throw new System.Exception("Item preview not rotating");
  invoke("HideModuleTooltip",null);if(studio.GetComponentInChildren<UnityEngine.Camera>(true).enabled)throw new System.Exception("Hidden item camera still renders");
  int itemStudios=0,meshes=0;foreach(var t in viewer.GetComponentsInChildren<UnityEngine.Transform>(true))if(t.name=="Module inspection studio"&&t.gameObject.activeInHierarchy){itemStudios++;meshes+=t.GetComponentsInChildren<UnityEngine.MeshRenderer>().Length;}
  if(itemStudios!=1||meshes!=1)throw new System.Exception("Item preview contains extra studios or meshes: "+itemStudios+" / "+meshes);
  report["single_character_studio_and_rotating_item_lifetime"]=true;
  if(originalDraft!="null"&&originalDraft!=""&&UnityEngine.JsonUtility.ToJson(field("characterDraft"))!=originalDraft)throw new System.Exception("Operator character draft changed");
  if(!string.IsNullOrEmpty(originalWorldDraft)&&(string)field("buildDraftReload")!=originalWorldDraft)throw new System.Exception("Operator world draft changed");
  report["drafts_preserved"]=true;report["passed"]=true;
}
System.Func<System.Collections.IEnumerator,bool> advance=routine=>{try{return routine.MoveNext();}catch(System.Exception error){report["passed"]=false;report["error"]=error.ToString();UnityEngine.Debug.LogError(error);return false;}};
System.Collections.IEnumerator Verify(){
 var routine=VerifySteps();
 try{while(advance(routine))yield return routine.Current;}
 finally{
  (routine as System.IDisposable)?.Dispose();
  invoke("HideModuleTooltip",null);invoke("SetCharacterOpen",new object[]{originalCharacter});invoke("ShSetMode",new object[]{originalBuild});type.GetField("shTab",flags).SetValue(viewer,originalTab);
  type.GetField("cinema",flags).SetValue(viewer,originalCinema);type.GetField("memoryFlyout",flags).SetValue(viewer,originalMemory);
  var path=System.IO.Path.GetFullPath(UnityEngine.Application.dataPath+"/../../t-scan/runtime_data/verification/ui-cleanup.json");System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(path));System.IO.File.WriteAllText(path,Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented));
  UnityEngine.Debug.Log("Viewer cleanup QA: "+Newtonsoft.Json.JsonConvert.SerializeObject(report));
 }
}
viewer.StartCoroutine(Verify());
