using UnityEngine;
namespace Steve.TScan {
 [DefaultExecutionOrder(110),RequireComponent(typeof(SteveBody))]
 public sealed class SteveBridge:MonoBehaviour {
  public string Endpoint="http://127.0.0.1:8765";
  public void Pause()=>GetComponent<SteveBody>().Bench?.Stop();
 }
}
