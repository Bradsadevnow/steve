using System;
using UnityEngine;

namespace Steve.TScan {
 [Serializable] public class MeadowManifest {
  public string schema="meadow-world-v1",world_id="steve_grid_v1";
  public int revision=1,columns=10,rows=10;
  public GridLandmark[] landmarks=Array.Empty<GridLandmark>();
 }

 [CreateAssetMenu(menuName="Steve/Meadow world definition")]
 public sealed class MeadowWorldDefinition:ScriptableObject {
  public MeadowManifest manifest=new MeadowManifest();
  public string ManifestJson=>JsonUtility.ToJson(manifest);
 }
}
