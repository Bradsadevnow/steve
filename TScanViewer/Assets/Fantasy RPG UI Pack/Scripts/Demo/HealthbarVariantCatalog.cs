using System;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoonTribe.UI
{
 [CreateAssetMenu(menuName="Moon Tribe/Healthbar Variants")]
 public class HealthbarVariantCatalog:ScriptableObject
 {
  [Serializable] public class Entry
  {
   public string id;
   public GameObject canvasPlain,canvasShader;
   public VisualTreeAsset toolkitPlain,toolkitShader;
  }
  public Entry[] entries=Array.Empty<Entry>();
 }
}
