using System;
using System.Collections.Generic;
using UnityEngine;

namespace TerraMageTD
{
    [DisallowMultipleComponent]
    public sealed class TerraMageWeaponLoadout : MonoBehaviour
    {
        private const int MaxWheelSlots = 10;

        [SerializeField] private List<TerraMageWeaponDefinition> assignedWeapons = new List<TerraMageWeaponDefinition>();
        [SerializeField] private int selectedSlotIndex;

        public event Action LoadoutChanged;
        public event Action<int, TerraMageWeaponDefinition> SelectionChanged;

        public int MaxSlots => MaxWheelSlots;
        public int ActiveSlotCount => assignedWeapons.Count;
        public int SelectedSlotIndex => selectedSlotIndex;
        public TerraMageWeaponDefinition CurrentWeapon => GetWeapon(selectedSlotIndex);

        private void Awake()
        {
            EnsureWeaponSlots();
            if (!IsDemoLoadoutConfigured())
            {
                ConfigureDemoLoadout();
            }
        }

        private void OnValidate()
        {
            EnsureWeaponSlots();
            selectedSlotIndex = Mathf.Clamp(selectedSlotIndex, 0, assignedWeapons.Count - 1);
        }

        public void ConfigureDemoLoadout()
        {
            assignedWeapons = new List<TerraMageWeaponDefinition>
            {
                TerraMageWeaponDefinition.CreateMelee(
                    "stone_gauntlet",
                    "Stone Gauntlet",
                    TerraMageMeleeRangeProfile.ShortStaff,
                    TerraMageMeleeGesture.Punch,
                    1.35f,
                    new Color(0.78f, 0.66f, 0.42f, 0.95f),
                    "Close-range melee gauntlet"),
                TerraMageWeaponDefinition.CreateRanged(
                    "shard_sling",
                    "Shard Sling",
                    13f,
                    24f,
                    3.2f,
                    0.8f,
                    new Color(0.4f, 0.72f, 1f, 0.95f),
                    "Ranged sling for Terra Mage material attacks")
            };

            selectedSlotIndex = 0;
            RaiseLoadoutChanged();
        }

        public TerraMageWeaponDefinition GetWeapon(int slotIndex)
        {
            EnsureWeaponSlots();

            if (slotIndex < 0 || slotIndex >= assignedWeapons.Count)
            {
                return assignedWeapons[0];
            }

            return assignedWeapons[slotIndex];
        }

        public bool IsSlotLocked(int slotIndex)
        {
            return false;
        }

        public bool AssignWeapon(int slotIndex, TerraMageWeaponDefinition weapon)
        {
            EnsureWeaponSlots();
            if (weapon == null || slotIndex < 0 || slotIndex >= MaxWheelSlots)
            {
                return false;
            }

            if (slotIndex < assignedWeapons.Count)
            {
                assignedWeapons[slotIndex] = weapon;
                RaiseLoadoutChanged();
                return true;
            }

            if (slotIndex == assignedWeapons.Count)
            {
                assignedWeapons.Add(weapon);
                RaiseLoadoutChanged();
                return true;
            }

            return false;
        }

        public bool AssignWeaponToNextFreeSlot(TerraMageWeaponDefinition weapon)
        {
            return AssignWeapon(assignedWeapons.Count, weapon);
        }

        public bool RemoveWeapon(int slotIndex)
        {
            EnsureWeaponSlots();
            if (slotIndex < 0 || slotIndex >= assignedWeapons.Count)
            {
                return false;
            }

            assignedWeapons.RemoveAt(slotIndex);
            EnsureWeaponSlots();
            selectedSlotIndex = Mathf.Clamp(selectedSlotIndex, 0, assignedWeapons.Count - 1);
            RaiseLoadoutChanged();
            return true;
        }

        public void SelectSlot(int slotIndex)
        {
            EnsureWeaponSlots();
            int clampedSlot = Mathf.Clamp(slotIndex, 0, assignedWeapons.Count - 1);
            selectedSlotIndex = clampedSlot;
            SelectionChanged?.Invoke(selectedSlotIndex, CurrentWeapon);
        }

        private void EnsureWeaponSlots()
        {
            if (assignedWeapons == null)
            {
                assignedWeapons = new List<TerraMageWeaponDefinition>();
            }

            if (assignedWeapons.Count == 0)
            {
                assignedWeapons.Add(TerraMageWeaponDefinition.CreateMelee(
                    "stone_gauntlet",
                    "Stone Gauntlet",
                    TerraMageMeleeRangeProfile.ShortStaff,
                    TerraMageMeleeGesture.Punch,
                    1.35f,
                    new Color(0.78f, 0.66f, 0.42f, 0.95f),
                    "Close-range melee gauntlet"));
            }

            for (int index = assignedWeapons.Count - 1; index >= 1; index--)
            {
                if (assignedWeapons[index] == null)
                {
                    assignedWeapons.RemoveAt(index);
                }
            }

            if (assignedWeapons.Count > MaxWheelSlots)
            {
                assignedWeapons.RemoveRange(MaxWheelSlots, assignedWeapons.Count - MaxWheelSlots);
            }
        }

        private void RaiseLoadoutChanged()
        {
            SelectionChanged?.Invoke(selectedSlotIndex, CurrentWeapon);
            LoadoutChanged?.Invoke();
        }

        private bool IsDemoLoadoutConfigured()
        {
            return assignedWeapons.Count == 2
                && assignedWeapons[0] != null
                && assignedWeapons[0].WeaponId == "stone_gauntlet"
                && assignedWeapons[1] != null
                && assignedWeapons[1].WeaponId == "shard_sling";
        }
    }
}
