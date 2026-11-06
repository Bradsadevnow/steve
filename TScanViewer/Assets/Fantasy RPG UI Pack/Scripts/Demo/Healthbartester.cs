using System.Collections.Generic;
using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif
namespace MoonTribe.UI
{
    [AddComponentMenu("Moon Tribe/Health Bar Tester")]
    public class HealthBarTester : MonoBehaviour
    {
        [SerializeField] List<HealthBarUGUI> bars = new List<HealthBarUGUI>();
        [SerializeField] bool autoFindInScene = true;
        [Tooltip("Percentage of maximum per second (works with both 0–1 and 0–100 resources).")]
        [SerializeField] float holdRate = 60;
        [SerializeField] bool showOnScreenHelp = true;
        float refreshAt;
        void Start() { if (autoFindInScene) RefreshBars(); }
        public void RefreshBars()
        {
            bars.Clear();
            bars.AddRange(FindObjectsByType<HealthBarUGUI>(FindObjectsInactive.Include));
            refreshAt = Time.unscaledTime + 1;
        }
        void Update()
        {
            if (autoFindInScene && Time.unscaledTime >= refreshAt) RefreshBars();
            bool left = false, right = false, full = false, empty = false, random = false;
#if ENABLE_INPUT_SYSTEM
            var k = Keyboard.current;
            if (k != null) { left = k.leftArrowKey.isPressed; right = k.rightArrowKey.isPressed;
                full = k.upArrowKey.wasPressedThisFrame; empty = k.downArrowKey.wasPressedThisFrame; random = k.rKey.wasPressedThisFrame; }
#elif ENABLE_LEGACY_INPUT_MANAGER
            left = Input.GetKey(KeyCode.LeftArrow); right = Input.GetKey(KeyCode.RightArrow);
            full = Input.GetKeyDown(KeyCode.UpArrow); empty = Input.GetKeyDown(KeyCode.DownArrow); random = Input.GetKeyDown(KeyCode.R);
#endif
            foreach (var bar in bars)
            {
                if (!bar || !bar.isActiveAndEnabled) continue;
                float delta = holdRate * .01f * bar.Model.Max * Time.unscaledDeltaTime;
                if (left) bar.Damage(delta); if (right) bar.Heal(delta);
                if (full) bar.SetValue(bar.Model.Max); if (empty) bar.SetValue(0);
                if (random) bar.SetValue(Random.value * bar.Model.Max);
            }
        }
        void OnGUI()
        {
            if (showOnScreenHelp) GUI.Box(new Rect(10, 10, 330, 82),
                "Health bars: Left / Right to drain / fill\nUp: full   Down: empty   R: random\nSpace: next demo panel");
        }
    }
}
