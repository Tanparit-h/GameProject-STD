using UnityEngine;

namespace SandMageTD
{
    public enum SandMageMaterialKind
    {
        DrySand,
        WetSand,
        PackedSand,
        Stone,
        MoltenGlass,
        Glass
    }

    public struct SandMageMaterialPayload
    {
        public SandMageMaterialKind Kind;
        public float Mass;
        public float Hardness;
        public float Heat;
        public Vector3 SourcePoint;

        public bool IsHot => Heat >= 1f || Kind == SandMageMaterialKind.MoltenGlass;
    }

    public static class SandMageMaterialSystem
    {
        public static SandMageMaterialPayload CreateLooseSand(Vector3 sourcePoint)
        {
            return new SandMageMaterialPayload
            {
                Kind = SandMageMaterialKind.DrySand,
                Mass = 1f,
                Hardness = 0.15f,
                Heat = 0f,
                SourcePoint = sourcePoint
            };
        }

        public static SandMageMaterialPayload Compress(SandMageMaterialPayload payload, float multiplier)
        {
            payload.Kind = payload.Kind == SandMageMaterialKind.Stone
                ? SandMageMaterialKind.Stone
                : SandMageMaterialKind.PackedSand;
            payload.Mass *= Mathf.Max(1f, multiplier);
            payload.Hardness = Mathf.Max(payload.Hardness, 0.7f);
            return payload;
        }

        public static SandMageMaterialPayload Heat(SandMageMaterialPayload payload, float heatAmount)
        {
            payload.Heat += Mathf.Max(0f, heatAmount);
            if ((payload.Kind == SandMageMaterialKind.DrySand || payload.Kind == SandMageMaterialKind.PackedSand) && payload.Heat >= 1f)
            {
                payload.Kind = SandMageMaterialKind.MoltenGlass;
                payload.Hardness = 0.05f;
            }

            return payload;
        }

        public static float CalculateImpactDamage(SandMageMaterialPayload payload, Vector3 velocity, float impactAngle01)
        {
            float velocityDamage = velocity.magnitude * payload.Mass;
            float hardnessDamage = payload.Hardness * 10f;
            float heatDamage = payload.Heat * 5f;
            return (velocityDamage + hardnessDamage + heatDamage) * Mathf.Clamp01(impactAngle01);
        }
    }
}
