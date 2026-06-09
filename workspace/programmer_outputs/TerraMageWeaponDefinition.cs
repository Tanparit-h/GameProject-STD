using System;
using UnityEngine;

namespace TerraMageTD
{
    public enum TerraMageWeaponAttackMode
    {
        Melee,
        Ranged
    }

    [Serializable]
    public sealed class TerraMageWeaponDefinition
    {
        [SerializeField] private string weaponId = "bare_hands";
        [SerializeField] private string displayName = "Bare Hands";
        [SerializeField] private TerraMageWeaponAttackMode attackMode = TerraMageWeaponAttackMode.Melee;
        [SerializeField] private TerraMageMeleeRangeProfile meleeProfile = TerraMageMeleeRangeProfile.UnarmedPunch;
        [SerializeField] private TerraMageMeleeGesture primaryGesture = TerraMageMeleeGesture.Punch;
        [SerializeField] private float meleeReach = 1.15f;
        [SerializeField] private float rangedPullRange = 8f;
        [SerializeField] private float rangedThrowForce = 14f;
        [SerializeField] private float rangedCompressMultiplier = 2.5f;
        [SerializeField] private float rangedHeatPerUse = 0.55f;
        [SerializeField] private Color uiColor = new Color(0.9f, 0.9f, 0.92f, 0.92f);
        [SerializeField] private string debugSummary = "Default Terra Mage weapon";

        public string WeaponId => weaponId;
        public string DisplayName => displayName;
        public TerraMageWeaponAttackMode AttackMode => attackMode;
        public TerraMageMeleeRangeProfile MeleeProfile => meleeProfile;
        public TerraMageMeleeGesture PrimaryGesture => primaryGesture;
        public float MeleeReach => meleeReach;
        public float RangedPullRange => rangedPullRange;
        public float RangedThrowForce => rangedThrowForce;
        public float RangedCompressMultiplier => rangedCompressMultiplier;
        public float RangedHeatPerUse => rangedHeatPerUse;
        public Color UiColor => uiColor;
        public string DebugSummary => debugSummary;
        public bool SupportsMelee => attackMode == TerraMageWeaponAttackMode.Melee;
        public bool SupportsRanged => attackMode == TerraMageWeaponAttackMode.Ranged;

        public static TerraMageWeaponDefinition CreateBareHands()
        {
            return new TerraMageWeaponDefinition
            {
                weaponId = "bare_hands",
                displayName = "Bare Hands",
                attackMode = TerraMageWeaponAttackMode.Melee,
                meleeProfile = TerraMageMeleeRangeProfile.UnarmedPunch,
                primaryGesture = TerraMageMeleeGesture.Punch,
                meleeReach = 1.15f,
                uiColor = new Color(0.92f, 0.92f, 0.95f, 0.95f),
                debugSummary = "Locked slot 0 punch profile"
            };
        }

        public static TerraMageWeaponDefinition CreateMelee(
            string id,
            string name,
            TerraMageMeleeRangeProfile profile,
            TerraMageMeleeGesture gesture,
            float reach,
            Color color,
            string summary)
        {
            return new TerraMageWeaponDefinition
            {
                weaponId = id,
                displayName = name,
                attackMode = TerraMageWeaponAttackMode.Melee,
                meleeProfile = profile,
                primaryGesture = gesture,
                meleeReach = Mathf.Max(0.6f, reach),
                uiColor = color,
                debugSummary = summary
            };
        }

        public static TerraMageWeaponDefinition CreateRanged(
            string id,
            string name,
            float pullRange,
            float throwForce,
            float compressMultiplier,
            float heatPerUse,
            Color color,
            string summary)
        {
            return new TerraMageWeaponDefinition
            {
                weaponId = id,
                displayName = name,
                attackMode = TerraMageWeaponAttackMode.Ranged,
                meleeProfile = TerraMageMeleeRangeProfile.ShortStaff,
                primaryGesture = TerraMageMeleeGesture.None,
                meleeReach = 0.95f,
                rangedPullRange = Mathf.Max(1f, pullRange),
                rangedThrowForce = Mathf.Max(1f, throwForce),
                rangedCompressMultiplier = Mathf.Max(1f, compressMultiplier),
                rangedHeatPerUse = Mathf.Max(0f, heatPerUse),
                uiColor = color,
                debugSummary = summary
            };
        }
    }
}
