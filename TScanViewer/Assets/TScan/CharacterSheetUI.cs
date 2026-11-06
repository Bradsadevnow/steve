using UnityEngine;
using UnityEngine.UIElements;

namespace Steve.TScan {
 public sealed partial class TScanViewer {
  static void SheetRect(VisualElement e,float x,float y,float width,float height){e.style.position=Position.Absolute;e.style.left=x;e.style.top=y;e.style.width=width;e.style.height=height;}
  void BuildEquipmentSheet(VisualElement parent){
   var fit=new MoonTribe.UI.PaintedFrame{DesignWidth=1200,DesignHeight=692,MaxScale=0};fit.AddToClassList("character-sheet");parent.Add(fit);
   var board=BxEl("sheet-artboard",fit);board.style.backgroundImage=new StyleBackground(Resources.Load<Texture2D>("UI/FantasyArt/decor_67"));
   var title=BxLabel("EQUIPMENT","sheet-heading",board);SheetRect(title,36,93,520,30);
   var libraryTitle=BxLabel("MODULE LIBRARY","sheet-heading",board);SheetRect(libraryTitle,655,93,480,30);
   var preview=BxEl("sheet-preview",board);preview.name="character-preview";SheetRect(preview,140,135,330,475);
   preview.RegisterCallback<PointerDownEvent>(e=>{if(e.button!=0)return;characterRotating=true;characterPointer=e.position;preview.CapturePointer(e.pointerId);e.StopPropagation();});
   preview.RegisterCallback<PointerMoveEvent>(e=>{if(!characterRotating)return;characterYaw-=(e.position.x-characterPointer.x)*.5f;characterPointer=e.position;if(characterPreview)characterPreview.transform.localRotation=Quaternion.Euler(0,characterYaw,0);e.StopPropagation();});
   preview.RegisterCallback<PointerUpEvent>(e=>{characterRotating=false;preview.ReleasePointer(e.pointerId);e.StopPropagation();});
   preview.RegisterCallback<PointerCaptureOutEvent>(_=>characterRotating=false);
   preview.RegisterCallback<WheelEvent>(e=>{ZoomCharacter(Mathf.Exp(e.delta.y*.025f));e.StopPropagation();});
   preview.RegisterCallback<GeometryChangedEvent>(_=>ResizeCharacterPreview(preview));
   characterSlots=BxEl("sheet-slots",board);characterSlots.pickingMode=PickingMode.Ignore;SheetRect(characterSlots,0,0,610,692);
   var library=new ScrollView(ScrollViewMode.Vertical){horizontalScrollerVisibility=ScrollerVisibility.Hidden};library.AddToClassList("character-library");SheetRect(library,650,135,490,475);board.Add(library);characterModules=library.contentContainer;
  }
  void PositionSheetSlot(Button button,int index){
   var points=new[]{new Vector2(30,130),new Vector2(485,130),new Vector2(30,255),new Vector2(485,255),new Vector2(30,380),new Vector2(485,380),new Vector2(485,505)};
   var p=points[Mathf.Clamp(index,0,points.Length-1)];SheetRect(button,p.x,p.y,90,110);
  }
  void ZoomCharacter(float factor){characterZoom=Mathf.Clamp(characterZoom*factor,.3f,2.5f);if(characterCamera)characterCamera.orthographicSize=characterFit*characterZoom;}
  void ResizeCharacterPreview(VisualElement preview){
   if(!characterCamera)return;int width=Mathf.Max(64,Mathf.RoundToInt(preview.layout.width*2)),height=Mathf.Max(64,Mathf.RoundToInt(preview.layout.height*2));
   if(characterTexture&&characterTexture.width==width&&characterTexture.height==height)return;
   characterCamera.targetTexture=null;if(characterTexture){characterTexture.Release();Destroy(characterTexture);}
   characterTexture=new RenderTexture(width,height,24){name="Character preview",hideFlags=HideFlags.DontSave};characterCamera.targetTexture=characterTexture;
   preview.style.backgroundImage=new StyleBackground(Background.FromRenderTexture(characterTexture));FitCharacterPreview();
  }
  void FitCharacterPreview(){
   if(!characterPreview||!characterCamera)return;var renderers=characterPreview.GetComponentsInChildren<Renderer>();if(renderers.Length==0)return;
   var bounds=renderers[0].bounds;foreach(var renderer in renderers)bounds.Encapsulate(renderer.bounds);
   var center=bounds.center-characterStage.transform.position;characterCamera.transform.localPosition=center+Vector3.back*7;
   characterFit=Mathf.Max(bounds.extents.y,bounds.extents.x/Mathf.Max(.1f,characterCamera.aspect))*1.12f;characterCamera.orthographicSize=characterFit*characterZoom;
  }
 }
}
