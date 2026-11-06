using System.Linq;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Steve.TScan {
 // Runtime world builder: a palette of classified kit pieces, paint/erase on the 15 x 15 grid, preview as a draft,
 // and Apply to publish a new manifest revision. The backend validates roles and blocking again on publish.
 public sealed partial class TScanViewer {
  enum BuildTool {Piece,Spawn,Flag,Erase}
  [SerializeField,HideInInspector] bool buildOpen;
  WorldBuilder builder;MeadowEnvironment buildEnv;GridWorkbench buildBench;Camera buildCamera;
  [SerializeField] string buildDraftReload="";
  BuildTool buildTool=BuildTool.Piece;
  string selectedPiece="",flagColor="blue",packFilter="",roleFilter="",saveName="my-world",buildStatus="";
  bool buildProblem;int buildYaw;Vector2 paletteScroll;string[] savedWorlds=new string[0];
  int hoverCol,hoverRow;bool hoverCell,hoverValid;
  GameObject cursorRoot,ghost;Material ghostMaterial,outlineMaterial;MeshFilter ghostFilter;Renderer outlineRenderer;
  public bool BuildDirty=>builder!=null&&builder.Dirty;

  void ToggleBuild(){
   if(buildOpen){buildOpen=false;HideCursor();ShowPublishedWorld();return;}
   buildEnv=FindAnyObjectByType<MeadowEnvironment>();buildBench=FindAnyObjectByType<GridWorkbench>();
   if(buildEnv==null||buildEnv.definition==null){buildStatus="No world definition in the scene.";buildProblem=true;buildOpen=true;return;}
   WorldKit.EnsureLoaded();
   // Edit a runtime copy so the shipped World.asset is never modified, in the editor or in a build.
   if(!buildEnv.definition.name.EndsWith(" (runtime)")){var copy=Instantiate(buildEnv.definition);copy.name=buildEnv.definition.name+" (runtime)";buildEnv.definition=copy;}
   EnsureBuildDraft();
   if(string.IsNullOrEmpty(selectedPiece))selectedPiece=WorldKit.Pieces.Where(p=>WorldKit.IsPlaceable(p)&&p.role==WorldKit.WallRole).OrderBy(p=>p.id).Select(p=>p.id).FirstOrDefault()??"";
   savedWorlds=WorldBuilder.SavedNames();buildOpen=true;RefreshPreview();buildStatus=bxDirtyNow?"Draft not applied yet.":"";buildProblem=false;
  }

  Vector2 ToGui(Vector2 screen)=>new Vector2(screen.x/UIScale,(Screen.height-screen.y)/UIScale-MessageHeight);
  bool PickCell(Vector2 screen,out int col,out int row){
   col=row=0;if(buildCamera==null)buildCamera=FindAnyObjectByType<SteveBody>()?.BodyCamera;if(buildCamera==null||buildEnv==null)return false;
   var ray=buildCamera.ScreenPointToRay(screen);var ground=new Plane(buildEnv.transform.up,buildEnv.transform.position);
   if(!ground.Raycast(ray,out float distance))return false;
   var local=buildEnv.transform.InverseTransformPoint(ray.GetPoint(distance));
   col=Mathf.RoundToInt((local.x+16f)/2f);row=Mathf.RoundToInt((local.z+16f)/2f);return WorldBuilder.InBoard(col,row);
  }

  bool RunTool(int col,int row,bool commit,out string why){
   switch(buildTool){
    case BuildTool.Spawn:return builder.TrySpawn(col,row,commit,out why);
    case BuildTool.Flag:return builder.TryFlag(flagColor,col,row,commit,out why);
    case BuildTool.Erase:return builder.TryErase(col,row,commit,out why);
    default:return builder.TryPlace(WorldKit.Info(selectedPiece),col,row,buildYaw,commit,out why);
   }
  }

  void RefreshPreview(){buildEnv.Override=builder.ToManifest(buildEnv.definition.manifest.revision);buildEnv.Rebuild();}
  void ShowPublishedWorld(){if(buildEnv&&buildEnv.Override!=null){buildEnv.Override=null;buildEnv.Rebuild();}}
  void EnsureBuildDraft(){
   if(builder!=null||!buildEnv||!buildEnv.definition)return;
   if(!string.IsNullOrEmpty(buildDraftReload)){
    builder=new WorldBuilder(JsonUtility.FromJson<MeadowManifest>(buildDraftReload));
    bxBaseline=JsonUtility.ToJson(new WorldBuilder(buildEnv.definition.manifest).ToManifest(0));RefreshDirty();
   }else{builder=new WorldBuilder(buildEnv.definition.manifest);builder.MarkClean();SetBaseline();}
  }

  void UpdateBuilder(){
   if(buildOpen){if(!buildEnv)buildEnv=FindAnyObjectByType<MeadowEnvironment>();if(!buildBench)buildBench=FindAnyObjectByType<GridWorkbench>();}
   if(!string.IsNullOrEmpty(buildDraftReload))EnsureBuildDraft();
   if(!buildOpen)ShowPublishedWorld();
   if(buildOpen&&buildEnv!=null&&bxRoot==null){
    builder=new WorldBuilder(!string.IsNullOrEmpty(buildDraftReload)?JsonUtility.FromJson<MeadowManifest>(buildDraftReload):buildEnv.definition.manifest);
    if(string.IsNullOrEmpty(buildDraftReload)){builder.MarkClean();SetBaseline();}RefreshPreview();RefreshDirty();
   }
   UpdateBuildUI();
   var mouse=Mouse.current;
   if(!buildOpen||characterOpen||worldApplying||builder==null||buildEnv==null||mouse==null){HideCursor();return;}
   var keyboard=Keyboard.current;
   if(keyboard!=null&&GUIUtility.keyboardControl==0&&!BxTyping()){
    bool ctrl=keyboard.leftCtrlKey.isPressed||keyboard.rightCtrlKey.isPressed;
    if(ctrl){if(keyboard.zKey.wasPressedThisFrame)Undo();if(keyboard.yKey.wasPressedThisFrame)Redo();}
    else{
     if(keyboard.qKey.wasPressedThisFrame)RotateYaw(-90);
     if(keyboard.eKey.wasPressedThisFrame||keyboard.rKey.wasPressedThisFrame)RotateYaw(90);
     if(keyboard.bKey.wasPressedThisFrame)SelectBuildTool(BuildTool.Piece);
     if(keyboard.tabKey.wasPressedThisFrame)TogglePieces();
     if(keyboard.pKey.wasPressedThisFrame)SelectBuildTool(BuildTool.Spawn);
     if(keyboard.fKey.wasPressedThisFrame)SelectBuildTool(BuildTool.Flag);
     if(keyboard.xKey.wasPressedThisFrame||keyboard.deleteKey.wasPressedThisFrame)SelectBuildTool(BuildTool.Erase);
     for(int i=0;i<9;i++)if(keyboard[(Key)((int)Key.Digit1+i)].wasPressedThisFrame)SelectSlot(i);
    }
   }
   Vector2 screen=mouse.position.ReadValue();
   bool overUi=OverUI(screen);
   bool inWorld=WorldInputContains(screen)&&!overUi;
   hoverCell=inWorld&&PickCell(screen,out hoverCol,out hoverRow);
   string why=null;hoverValid=hoverCell&&RunTool(hoverCol,hoverRow,false,out why);
   UpdateCursor();
   if(buildClick&&hoverCell){
    if(hoverValid){
     PushUndo();
     RunTool(hoverCol,hoverRow,true,out why);RefreshPreview();AfterEdit();
    }else{buildStatus=why??"Cannot do that there.";buildProblem=true;}
   }
  }

  void EnsureCursor(){
   if(cursorRoot!=null||buildEnv==null)return;
   cursorRoot=new GameObject("Build cursor"){layer=30,hideFlags=HideFlags.DontSave};cursorRoot.transform.SetParent(buildEnv.transform,false);
   ghostMaterial=new Material(Shader.Find("Steve/MeadowVertex")){hideFlags=HideFlags.DontSave};
   ghost=new GameObject("Ghost piece"){layer=30,hideFlags=HideFlags.DontSave};ghost.transform.SetParent(cursorRoot.transform,false);ghostFilter=ghost.AddComponent<MeshFilter>();ghost.AddComponent<MeshRenderer>().sharedMaterial=ghostMaterial;
   outlineMaterial=new Material(Shader.Find("Universal Render Pipeline/Unlit")){hideFlags=HideFlags.DontSave};
   var quad=GameObject.CreatePrimitive(PrimitiveType.Quad);quad.name="Cell outline";quad.layer=30;quad.hideFlags=HideFlags.DontSave;Destroy(quad.GetComponent<Collider>());
   quad.transform.SetParent(cursorRoot.transform,false);quad.transform.localRotation=Quaternion.Euler(90,0,0);quad.transform.localPosition=new Vector3(0,.04f,0);quad.transform.localScale=new Vector3(1.9f,1.9f,1);
   outlineRenderer=quad.GetComponent<Renderer>();outlineRenderer.sharedMaterial=outlineMaterial;outlineRenderer.shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;
  }
  void UpdateCursor(){
   EnsureCursor();if(cursorRoot==null)return;
   cursorRoot.SetActive(hoverCell);if(!hoverCell)return;
   cursorRoot.transform.localPosition=MeadowEnvironment.Cell(hoverCol,hoverRow);
   outlineMaterial.SetColor("_BaseColor",hoverValid?new Color(.2f,.9f,.85f):new Color(.95f,.25f,.25f));
   var info=buildTool==BuildTool.Piece?WorldKit.Info(selectedPiece):null;
   ghost.SetActive(info!=null&&hoverValid);
   float cells=info!=null?WorldKit.FootprintOf(info):1;outlineRenderer.transform.localScale=new Vector3(1.9f*cells+(cells>1?.2f:0),1.9f*cells+(cells>1?.2f:0),1);
   if(info!=null){ghostFilter.sharedMesh=WorldKit.MeshOf(info.id);ghost.transform.localRotation=Quaternion.Euler(0,info.role==WorldKit.FloorRole?0:buildYaw,0);ghost.transform.localPosition=Vector3.up*(info.role==WorldKit.FloorRole?.03f:0);}
  }
  void HideCursor(){if(cursorRoot!=null)cursorRoot.SetActive(false);hoverCell=false;}

  // At startup, resume the last applied world so Unity publishes a revision the backend will accept.
  void LoadAppliedWorld(){
   var env=FindAnyObjectByType<MeadowEnvironment>();if(env==null||env.definition==null)return;
   var saved=WorldBuilder.LoadCurrent(env.definition.manifest.revision);if(saved==null)return;
   var copy=Instantiate(env.definition);copy.name=env.definition.name+" (runtime)";copy.manifest=saved;env.definition=copy;
  }

  bool worldApplying;
  void ApplyBuild(){if(!worldApplying)StartCoroutine(ApplyBuildConfirmed());}
  System.Collections.IEnumerator ApplyBuildConfirmed(){
   var lost=builder.Unreachable();if(lost!=null){buildStatus=lost+" Fix the layout before applying.";buildProblem=true;yield break;}
   if(buildBench==null||buildBench.State==null||buildBench.State.running||buildBench.Busy||sending){buildStatus="Stop Steve and wait for backend/presentation before applying.";buildProblem=true;yield break;}
   int next=buildEnv.definition.manifest.revision+1;
   var draft=builder.ToManifest(next);worldApplying=true;buildProblem=false;buildStatus="Awaiting backend confirmation…";bool accepted=false;
   yield return buildBench.PublishWorld(draft,(ok,message)=>{accepted=ok;buildStatus=message;});
   worldApplying=false;
   if(!accepted){buildProblem=true;yield break;}
   buildEnv.definition.manifest=draft;buildEnv.Override=null;buildEnv.Rebuild();builder.MarkClean();SetBaseline();WorldBuilder.SaveCurrent(draft);buildStatus="Applied · confirmed world revision "+next;
  }
  void RevertBuild(){
   builder.Load(buildEnv.definition.manifest);builder.MarkClean();SetBaseline();buildEnv.Override=null;buildEnv.Rebuild();buildStatus="Reverted to the published world.";buildProblem=false;
  }

  static int RoleRank(string role)=>System.Array.IndexOf(new[]{"floor","wall","obstacle","structure","hazard","decor","actor","boss"},role);
  static string ShortPack(string pack)=>pack=="dungeon"?"Dungeon":pack=="swap"?"Swap meet":pack=="school"?"School":WorldKit.PackTitle(pack);
 }
}
