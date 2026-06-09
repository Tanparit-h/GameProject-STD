using UnityEngine;

namespace TerraMageTD
{
    public enum TerraMageMaterialKind
    {
        LooseEarth,
        SoftEarth,
        PackedEarth,
        Stone,
        MoltenGlass,
        Glass
    }

    public struct TerraMageMaterialPayload
    {
        public TerraMageMaterialKind Kind;
        public float Mass;
        public float Hardness;
        public float Heat;
        public Vector3 SourcePoint;

        public bool IsHot => Heat >= 1f || Kind == TerraMageMaterialKind.MoltenGlass;
    }

    public static class TerraMageMaterialSystem
    {
        public static TerraMageMaterialPayload CreateLooseEarth(Vector3 sourcePoint)
        {
            return new TerraMageMaterialPayload
            {
                Kind = TerraMageMaterialKind.LooseEarth,
                Mass = 1f,
                Hardness = 0.15f,
                Heat = 0f,
                SourcePoint = sourcePoint
            };
        }

        public static TerraMageMaterialPayload Compress(TerraMageMaterialPayload payload, float multiplier)
        {
            payload.Kind = payload.Kind == TerraMageMaterialKind.Stone
                ? TerraMageMaterialKind.Stone
                : TerraMageMaterialKind.PackedEarth;
            payload.Mass *= Mathf.Max(1f, multiplier);
            payload.Hardness = Mathf.Max(payload.Hardness, 0.7f);
            return payload;
        }

        public static TerraMageMaterialPayload Heat(TerraMageMaterialPayload payload, float heatAmount)
        {
            payload.Heat += Mathf.Max(0f, heatAmount);
            if ((payload.Kind == TerraMageMaterialKind.LooseEarth || payload.Kind == TerraMageMaterialKind.PackedEarth)
                && payload.Heat >= 1f)
            {
                payload.Kind = TerraMageMaterialKind.MoltenGlass;
                payload.Hardness = 0.05f;
            }

            return payload;
        }

        public static float CalculateImpactDamage(TerraMageMaterialPayload payload, Vector3 velocity, float impactAngle01)
        {
            float velocityDamage = velocity.magnitude * payload.Mass;
            float hardnessDamage = payload.Hardness * 10f;
            float heatDamage = payload.Heat * 5f;
            return (velocityDamage + hardnessDamage + heatDamage) * Mathf.Clamp01(impactAngle01);
        }
    }
}
