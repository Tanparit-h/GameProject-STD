using UnityEngine;

namespace TerraMageTD
{
    public static class TerraMagePlayerMechanics
    {
        public static Vector3 BuildCameraRelativeMove(Vector2 input, Transform basis, Transform fallback)
        {
            Vector2 clampedInput = Vector2.ClampMagnitude(input, 1f);
            Transform moveBasis = basis != null ? basis : fallback;
            Vector3 fallbackForward = fallback != null ? fallback.forward : Vector3.forward;
            Vector3 fallbackRight = fallback != null ? fallback.right : Vector3.right;

            Vector3 forward = moveBasis != null
                ? Vector3.ProjectOnPlane(moveBasis.forward, Vector3.up).normalized
                : fallbackForward;
            Vector3 right = moveBasis != null
                ? Vector3.ProjectOnPlane(moveBasis.right, Vector3.up).normalized
                : fallbackRight;

            if (forward.sqrMagnitude < 0.001f)
            {
                forward = fallbackForward;
            }

            if (right.sqrMagnitude < 0.001f)
            {
                right = fallbackRight;
            }

            return right * clampedInput.x + forward * clampedInput.y;
        }

        public static float ResolveMoveSpeed(bool running, float walkSpeed, float runSpeed)
        {
            return running ? runSpeed : walkSpeed;
        }

        public static float UpdateJumpBuffer(float currentTimer, bool jumpPressed, float bufferTime, float deltaTime)
        {
            return jumpPressed ? bufferTime : Mathf.Max(0f, currentTimer - deltaTime);
        }

        public static float UpdateCoyoteTimer(float currentTimer, bool grounded, float coyoteTime, float deltaTime)
        {
            return grounded ? coyoteTime : Mathf.Max(0f, currentTimer - deltaTime);
        }

        public static bool CanUseBufferedJump(float jumpBufferTimer, float coyoteTimer)
        {
            return jumpBufferTimer > 0f && coyoteTimer > 0f;
        }

        public static float CalculateJumpVelocity(float jumpHeight, float gravity)
        {
            return Mathf.Sqrt(Mathf.Max(0f, jumpHeight) * Mathf.Max(0f, -2f * gravity));
        }

        public static TerraMageMeleeGesture ClassifyMeleeGesture(Vector2 dragDelta, float threshold)
        {
            if (dragDelta.magnitude < threshold)
            {
                return TerraMageMeleeGesture.None;
            }

            if (Mathf.Abs(dragDelta.x) > Mathf.Abs(dragDelta.y))
            {
                return dragDelta.x < 0f ? TerraMageMeleeGesture.LeftSwing : TerraMageMeleeGesture.RightSwing;
            }

            return dragDelta.y > 0f ? TerraMageMeleeGesture.Overhead : TerraMageMeleeGesture.Punch;
        }

        public static float CalculateMeleeDamage(float baseDamage, TerraMageWeaponDefinition weapon)
        {
            float reachBonus = weapon != null ? weapon.MeleeReach * 2f : 0f;
            return Mathf.Max(0f, baseDamage + reachBonus);
        }

        public static Vector3 BuildMeleeOrigin(Transform actor, float heightOffset)
        {
            Vector3 basePosition = actor != null ? actor.position : Vector3.zero;
            return basePosition + Vector3.up * Mathf.Max(0f, heightOffset);
        }

        public static Vector3 ResolveAimDirection(Camera aimCamera, Transform fallback)
        {
            if (aimCamera != null)
            {
                return aimCamera.transform.forward;
            }

            return fallback != null ? fallback.forward : Vector3.forward;
        }

        public static float ResolvePullRange(TerraMageWeaponDefinition weapon, float defaultPullRange)
        {
            if (weapon == null || !weapon.SupportsRanged)
            {
                return 0f;
            }

            return weapon.RangedPullRange > 0f ? weapon.RangedPullRange : defaultPullRange;
        }

        public static float ResolveThrowForce(TerraMageWeaponDefinition weapon, float defaultThrowForce)
        {
            return weapon != null && weapon.SupportsRanged ? weapon.RangedThrowForce : defaultThrowForce;
        }

        public static float ResolveCompressMultiplier(TerraMageWeaponDefinition weapon, float defaultCompressMultiplier)
        {
            return weapon != null && weapon.SupportsRanged ? weapon.RangedCompressMultiplier : defaultCompressMultiplier;
        }

        public static float ResolveHeatPerUse(TerraMageWeaponDefinition weapon, float defaultHeatPerUse)
        {
            return weapon != null && weapon.SupportsRanged ? weapon.RangedHeatPerUse : defaultHeatPerUse;
        }

        public static TerraMageMaterialPayload CreateDefaultRangedPayload(Vector3 sourcePoint)
        {
            return TerraMageMaterialSystem.Compress(TerraMageMaterialSystem.CreateLooseEarth(sourcePoint), 1.6f);
        }

        public static Vector3 CalculateProjectileSpawnPosition(Camera aimCamera, float spawnOffset)
        {
            if (aimCamera == null)
            {
                return Vector3.zero;
            }

            return aimCamera.transform.position + aimCamera.transform.forward * Mathf.Max(0f, spawnOffset);
        }

        public static Color GetProjectileTint(TerraMageMaterialPayload payload)
        {
            return payload.Kind switch
            {
                TerraMageMaterialKind.MoltenGlass => new Color(1f, 0.42f, 0.15f, 1f),
                TerraMageMaterialKind.Glass => new Color(0.72f, 0.95f, 1f, 1f),
                TerraMageMaterialKind.Stone => new Color(0.45f, 0.48f, 0.52f, 1f),
                TerraMageMaterialKind.PackedEarth => new Color(0.48f, 0.34f, 0.18f, 1f),
                _ => new Color(0.62f, 0.48f, 0.28f, 1f),
            };
        }

        public static void ApplyProjectileTint(GameObject projectileObject, TerraMageMaterialPayload payload)
        {
            if (projectileObject == null)
            {
                return;
            }

            Color tint = GetProjectileTint(payload);
            foreach (Renderer rendererComponent in projectileObject.GetComponentsInChildren<Renderer>())
            {
                foreach (Material material in rendererComponent.materials)
                {
                    if (material != null && material.HasProperty("_Color"))
                    {
                        material.color = tint;
                    }
                }
            }
        }
    }
}
