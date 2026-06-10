using UnityEngine;

namespace TerraMageTD
{
    public static class TerraMagePlayerMechanics
    {
        private const int MaxLedgeProbeHits = 12;

        private static readonly RaycastHit[] LedgeProbeHits = new RaycastHit[MaxLedgeProbeHits];
        private static readonly RaycastHit[] LedgeTopHits = new RaycastHit[MaxLedgeProbeHits];

        public readonly struct LedgeGrab
        {
            public LedgeGrab(Vector3 hangPosition, Vector3 climbPosition, Vector3 facingDirection)
            {
                HangPosition = hangPosition;
                ClimbPosition = climbPosition;
                FacingDirection = facingDirection;
            }

            public Vector3 HangPosition { get; }
            public Vector3 ClimbPosition { get; }
            public Vector3 FacingDirection { get; }
        }

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

        public static float UpdateJumpDelayTimer(float currentTimer, float deltaTime)
        {
            return Mathf.Max(0f, currentTimer - deltaTime);
        }

        public static float CalculateJumpVelocity(float jumpHeight, float gravity)
        {
            return Mathf.Sqrt(Mathf.Max(0f, jumpHeight) * Mathf.Max(0f, -2f * gravity));
        }

        public static bool HasForwardParkourInput(float verticalInput)
        {
            return verticalInput > 0.25f;
        }

        public static bool HasBackwardParkourInput(float verticalInput)
        {
            return verticalInput < -0.25f;
        }

        public static bool TryFindLedgeGrab(
            Transform actor,
            Vector3 preferredDirection,
            float forwardCheckDistance,
            float forwardProbeHeight,
            float probeRadius,
            float topProbeHeight,
            float topProbeDepth,
            float hangBackOffset,
            float hangDownOffset,
            float climbForwardOffset,
            float standHeightOffset,
            LayerMask ledgeMask,
            out LedgeGrab grab)
        {
            grab = default;
            if (actor == null)
            {
                return false;
            }

            Vector3 direction = Vector3.ProjectOnPlane(preferredDirection, Vector3.up);
            if (direction.sqrMagnitude < 0.001f)
            {
                direction = Vector3.ProjectOnPlane(actor.forward, Vector3.up);
            }

            if (direction.sqrMagnitude < 0.001f)
            {
                return false;
            }

            direction.Normalize();
            if (!TryFindClosestForwardLedgeHit(
                    actor,
                    direction,
                    forwardCheckDistance,
                    forwardProbeHeight,
                    probeRadius,
                    ledgeMask,
                    out RaycastHit wallHit))
            {
                return false;
            }

            Vector3 topProbeOrigin =
                wallHit.point + (direction * Mathf.Max(0.01f, climbForwardOffset)) + (Vector3.up * topProbeHeight);
            if (!TryFindClosestTopLedgeHit(
                    actor,
                    topProbeOrigin,
                    topProbeDepth,
                    ledgeMask,
                    out RaycastHit topHit))
            {
                return false;
            }

            if (topHit.normal.y < 0.45f || topHit.point.y <= actor.position.y + 0.08f)
            {
                return false;
            }

            Vector3 hangPosition = topHit.point - (direction * Mathf.Max(0f, hangBackOffset))
                - (Vector3.up * Mathf.Max(0f, hangDownOffset));
            Vector3 climbPosition = topHit.point + (direction * Mathf.Max(0f, climbForwardOffset))
                + (Vector3.up * Mathf.Max(0f, standHeightOffset));
            grab = new LedgeGrab(hangPosition, climbPosition, direction);
            return true;
        }

        private static bool TryFindClosestForwardLedgeHit(
            Transform actor,
            Vector3 direction,
            float forwardCheckDistance,
            float forwardProbeHeight,
            float probeRadius,
            LayerMask ledgeMask,
            out RaycastHit bestHit)
        {
            bestHit = default;
            Vector3 forwardOrigin = actor.position + Vector3.up * Mathf.Max(0.01f, forwardProbeHeight);
            int hitCount = Physics.SphereCastNonAlloc(
                forwardOrigin,
                Mathf.Max(0.005f, probeRadius),
                direction,
                LedgeProbeHits,
                Mathf.Max(0.01f, forwardCheckDistance),
                ledgeMask,
                QueryTriggerInteraction.Ignore);

            float closestDistance = float.MaxValue;
            for (int hitIndex = 0; hitIndex < hitCount; hitIndex++)
            {
                RaycastHit hit = LedgeProbeHits[hitIndex];
                if (!IsUsableParkourHit(actor, hit.collider) || hit.distance >= closestDistance)
                {
                    continue;
                }

                closestDistance = hit.distance;
                bestHit = hit;
            }

            return closestDistance < float.MaxValue;
        }

        private static bool TryFindClosestTopLedgeHit(
            Transform actor,
            Vector3 topProbeOrigin,
            float topProbeDepth,
            LayerMask ledgeMask,
            out RaycastHit bestHit)
        {
            bestHit = default;
            int hitCount = Physics.RaycastNonAlloc(
                topProbeOrigin,
                Vector3.down,
                LedgeTopHits,
                Mathf.Max(0.01f, topProbeDepth),
                ledgeMask,
                QueryTriggerInteraction.Ignore);

            float closestDistance = float.MaxValue;
            for (int hitIndex = 0; hitIndex < hitCount; hitIndex++)
            {
                RaycastHit hit = LedgeTopHits[hitIndex];
                if (!IsUsableParkourHit(actor, hit.collider) || hit.distance >= closestDistance)
                {
                    continue;
                }

                closestDistance = hit.distance;
                bestHit = hit;
            }

            return closestDistance < float.MaxValue;
        }

        private static bool IsUsableParkourHit(Transform actor, Collider hitCollider)
        {
            return hitCollider != null
                && actor != null
                && !hitCollider.transform.IsChildOf(actor);
        }

        public static Vector3 MoveTowardLedgeAnchor(Vector3 currentPosition, Vector3 anchorPosition, float snapSpeed, float deltaTime)
        {
            return Vector3.MoveTowards(
                currentPosition,
                anchorPosition,
                Mathf.Max(0.01f, snapSpeed) * Mathf.Max(0f, deltaTime));
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
