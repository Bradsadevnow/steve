using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif
namespace DarkRPGUI
{
    public class mr_GM : MonoBehaviour
    {
        int index;
        GameObject currentPanel;
        [SerializeField] GameObject[] panels;
        void Start()
        {
            if (panels == null) return;
            foreach (var panel in panels) if (panel) panel.SetActive(false);
            SetActivePanel(0);
        }
        public void NextPanel() => SetActivePanel(index + 1);
        public void PrevPanel() => SetActivePanel(index - 1);
        void SetActivePanel(int value)
        {
            if (panels == null || panels.Length == 0) return;
            index = (value % panels.Length + panels.Length) % panels.Length;
            if (currentPanel) currentPanel.SetActive(false);
            currentPanel = panels[index];
            if (currentPanel) currentPanel.SetActive(true);
        }
        void Update()
        {
#if ENABLE_INPUT_SYSTEM
            if (Keyboard.current != null && Keyboard.current.spaceKey.wasPressedThisFrame) NextPanel();
#elif ENABLE_LEGACY_INPUT_MANAGER
            if (Input.GetKeyDown(KeyCode.Space)) NextPanel();
#endif
        }
    }
}
