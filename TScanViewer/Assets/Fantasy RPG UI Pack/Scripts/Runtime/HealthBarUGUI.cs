using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;

namespace MoonTribe.UI
{
    [AddComponentMenu("Moon Tribe/Health Bar (uGUI)")]
    public class HealthBarUGUI : MonoBehaviour
    {
        [System.Serializable] public class FloatEvent : UnityEvent<float> { }
        [Header("Values")]
        [SerializeField, Min(0.0001f)] float maxValue = 100f;
        [SerializeField, Min(0)] float startValue = 100f;
        [SerializeField, Min(0)] float smoothSpeed = 4f;
        [SerializeField] bool useUnscaledTime = true;
        [Header("Fill layers — retain painted proportions")]
        [SerializeField] Image fillBody;
        [SerializeField] Image[] additionalFills = new Image[0];
        [Header("Optional moving edge")]
        [SerializeField] RectTransform edge;
        [SerializeField] Vector2 edgeAtEmpty;
        [SerializeField] Vector2 edgeAtFull;
        [Tooltip("Derive the edge position from the fill rectangle when resized.")]
        [SerializeField] bool automaticEdgePosition = true;
        [SerializeField] bool hideEdgeAtBounds = true;
        public FloatEvent OnNormalizedChanged = new FloatEvent();
        public UnityEvent OnEmptied = new UnityEvent();
        public UnityEvent OnFilled = new UnityEvent();
        HealthBarModel _model;
        public HealthBarModel Model { get { EnsureInitialized(); return _model; } }
        public Image FillBody => fillBody;
        public Image[] AdditionalFills => additionalFills;
        public RectTransform Edge => edge;
        void EnsureInitialized()
        {
            if (_model != null) return;
            // Preserve scene-only prototypes that predate the multi-layer field.
            if (fillBody && (additionalFills == null || additionalFills.Length == 0))
            {
                var found = new System.Collections.Generic.List<Image>();
                foreach (var image in GetComponentsInChildren<Image>(true))
                    if (image != fillBody && image.rectTransform != edge && image.type == Image.Type.Filled
                        && image.GetComponentInParent<HealthBarUGUI>() == this) found.Add(image);
                additionalFills = found.ToArray();
            }
            _model = new HealthBarModel(maxValue, smoothSpeed);
            _model.SetCurrent(startValue, true);
            _model.Changed += Apply;
            _model.Emptied += NotifyEmpty;
            _model.Filled += NotifyFull;
            Apply(_model.Displayed);
        }
        void NotifyEmpty() => OnEmptied?.Invoke();
        void NotifyFull() => OnFilled?.Invoke();
        void Awake() => EnsureInitialized();
        void OnEnable() { EnsureInitialized(); Apply(_model.Displayed); }
        void Update() => Model.Tick(useUnscaledTime ? Time.unscaledDeltaTime : Time.deltaTime);
        void OnRectTransformDimensionsChange() { if (_model != null) Apply(_model.Displayed); }
        void OnDestroy()
        {
            if (_model == null) return;
            _model.Changed -= Apply;
            _model.Emptied -= NotifyEmpty;
            _model.Filled -= NotifyFull;
        }
        public void SetValue(float value) => Model.SetCurrent(value);
        public void SetValueInstant(float value) => Model.SetCurrent(value, true);
        public void SetMax(float max, bool keepRatio = false) => Model.SetMax(max, keepRatio);
        public void Damage(float amount) => Model.Change(-Mathf.Abs(amount));
        public void Heal(float amount) => Model.Change(Mathf.Abs(amount));
        void Apply(float value)
        {
            if (fillBody) fillBody.fillAmount = value;
            if (additionalFills != null)
                foreach (var image in additionalFills) if (image) image.fillAmount = LayerFill(image, value);
            if (edge)
            {
                if (automaticEdgePosition && fillBody && edge.parent)
                {
                    var rect = fillBody.rectTransform.rect;
                    bool vertical = fillBody.fillMethod == Image.FillMethod.Vertical;
                    float fraction = fillBody.fillOrigin == 1 ? 1 - value : value;
                    var point = vertical ? new Vector3(rect.center.x, Mathf.Lerp(rect.yMin, rect.yMax, fraction))
                        : new Vector3(Mathf.Lerp(rect.xMin, rect.xMax, fraction), rect.center.y);
                    var local = edge.parent.InverseTransformPoint(fillBody.rectTransform.TransformPoint(point));
                    var position = edge.localPosition;
                    if (vertical) position.y = local.y; else position.x = local.x;
                    edge.localPosition = position;
                }
                else edge.anchoredPosition = Vector2.Lerp(edgeAtEmpty, edgeAtFull, value);
                if (hideEdgeAtBounds) edge.gameObject.SetActive(value > 0 && value < 1);
            }
            OnNormalizedChanged?.Invoke(value);
        }
        float LayerFill(Image image, float value)
        {
            if (!fillBody || value <= 0 || value >= 1) return value;
            var body = fillBody.rectTransform;
            bool vertical = fillBody.fillMethod == Image.FillMethod.Vertical;
            float fraction = fillBody.fillOrigin == 1 ? 1 - value : value;
            var point = vertical ? new Vector3(body.rect.center.x, Mathf.Lerp(body.rect.yMin,body.rect.yMax,fraction))
                : new Vector3(Mathf.Lerp(body.rect.xMin,body.rect.xMax,fraction),body.rect.center.y);
            var local = image.rectTransform.InverseTransformPoint(body.TransformPoint(point));
            var r = image.rectTransform.rect;
            float n = vertical ? Mathf.InverseLerp(r.yMin,r.yMax,local.y) : Mathf.InverseLerp(r.xMin,r.xMax,local.x);
            return image.fillOrigin == 1 ? 1 - n : n;
        }
        [ContextMenu("Capture edge position → FULL")]
        void CaptureFull() { if (edge) edgeAtFull = edge.anchoredPosition; }
        [ContextMenu("Capture edge position → EMPTY")]
        void CaptureEmpty() { if (edge) edgeAtEmpty = edge.anchoredPosition; }
        [ContextMenu("Test: Damage 10%")]
        void TestDamage() { if (Application.isPlaying) Damage(Model.Max * 0.1f); }
        [ContextMenu("Test: Heal 10%")]
        void TestHeal() { if (Application.isPlaying) Heal(Model.Max * 0.1f); }
#if UNITY_EDITOR
        void OnValidate()
        {
            maxValue = Mathf.Max(0.0001f, maxValue);
            startValue = Mathf.Clamp(startValue, 0, maxValue);
            smoothSpeed = Mathf.Max(0, smoothSpeed);
        }
#endif
    }
}
