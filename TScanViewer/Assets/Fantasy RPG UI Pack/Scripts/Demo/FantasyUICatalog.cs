using System;
using UnityEngine;
using UnityEngine.UIElements;

namespace MoonTribe.UI
{
    [CreateAssetMenu(menuName = "Moon Tribe/UI Toolkit Catalog")]
    public class FantasyUICatalog : ScriptableObject
    {
        [Serializable] public class Entry
        {
            public string id;
            public string category;
            public VisualTreeAsset template;
        }
        public Entry[] entries = new Entry[0];
    }
}
