using System;
using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;
namespace Steve.TScan {
 public sealed partial class TScanViewer {
  VisualElement moduleTooltip,moduleTooltipImage,moduleTooltipDetails;Label moduleTooltipName;ModuleInspectPreview moduleInspectPreview;
  void BuildModuleTooltip(){
   moduleTooltip=BxEl("module-inspect glass",bxRoot);moduleTooltip.name="module-inspection";moduleTooltip.style.display=DisplayStyle.None;
   moduleTooltipName=BxLabel("","module-inspect-name",moduleTooltip);
   moduleTooltipImage=BxEl("module-inspect-image",moduleTooltip);
   var scroll=new ScrollView(ScrollViewMode.Vertical){horizontalScrollerVisibility=ScrollerVisibility.Hidden,verticalScrollerVisibility=ScrollerVisibility.Hidden};scroll.style.flexGrow=1;scroll.style.minHeight=0;moduleTooltip.Add(scroll);moduleTooltipDetails=scroll.contentContainer;
   foreach(var child in moduleTooltip.Query<VisualElement>().ToList())child.pickingMode=PickingMode.Ignore;moduleTooltip.pickingMode=PickingMode.Ignore;
  }
  void ShowModuleTooltip(CharacterModule module,VisualElement anchor){
   if(!CharacterBuilderVisible||moduleTooltip==null)return;
   moduleTooltipDetails.Clear();moduleTooltipName.text=module.name;
   BxLabel(string.Join(" / ",module.mount_types.Select(CharacterPresentation.Name))+" · "+module.slots+" mount"+(module.slots==1?"":"s"),"module-inspect-muted",moduleTooltipDetails);
   BxLabel("STATS","label-cap",moduleTooltipDetails);
   var bonuses=module.stat_modifiers??Array.Empty<CharacterStatModifier>();
   BxLabel(bonuses.Length==0?"No stat bonuses":string.Join("   ",bonuses.Select(s=>(s.amount>0?"+":"")+s.amount+" "+s.stat)),"module-inspect-text",moduleTooltipDetails);
   BxLabel("GRANTED ABILITIES","label-cap",moduleTooltipDetails);
   foreach(var ability in module.abilities??Array.Empty<CharacterAbilityView>()){
    BxLabel(ability.name,"module-inspect-text",moduleTooltipDetails);BxLabel(ability.description,"module-inspect-muted",moduleTooltipDetails);
   }
   if((module.abilities?.Length??0)==0)BxLabel("No granted abilities yet.","module-inspect-muted",moduleTooltipDetails);
   foreach(var child in moduleTooltip.Query<VisualElement>().ToList())child.pickingMode=PickingMode.Ignore;
   moduleInspectPreview??=new ModuleInspectPreview();moduleInspectPreview.Show(module,transform);moduleTooltipImage.style.backgroundImage=new StyleBackground(Background.FromRenderTexture(moduleInspectPreview.Texture));
   var origin=bxRoot.WorldToLocal(anchor.worldBound.position);float width=300,height=Mathf.Min(580,bxRoot.layout.height-24);float x=origin.x-width-12;if(x<8)x=origin.x+anchor.worldBound.width+12;
   moduleTooltip.style.left=Mathf.Clamp(x,8,Mathf.Max(8,bxRoot.layout.width-width-8));moduleTooltip.style.top=Mathf.Clamp(origin.y,8,Mathf.Max(8,bxRoot.layout.height-height-8));moduleTooltip.style.height=height;moduleTooltip.style.display=DisplayStyle.Flex;moduleTooltip.BringToFront();
  }
  void HideModuleTooltip(){if(moduleTooltip!=null)moduleTooltip.style.display=DisplayStyle.None;moduleInspectPreview?.Hide();}
 }
}
