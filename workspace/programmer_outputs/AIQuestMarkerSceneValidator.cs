using System;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class AIQuestMarkerSceneValidator
{
    private const string ScenePath = "Assets/Scenes/QuestMarkerScene.unity";

    public static void ValidateScene()
    {
        EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);

        RequireObject("AIQuest_Ground");
        var player = RequireObject("AIQuest_Player");
        RequireObject("AIQuest_PlayerMarker");
        var markerVisual = RequireObject("AIQuest_MarkerVisual");
        var objectiveObject = RequireObject("AIQuest_Objective");

        var tracker = RequireComponent<QuestMarkerTracker>(player, "AIQuest_Player");
        var objective = RequireComponent<QuestMarkerObjective>(objectiveObject, "AIQuest_Objective");
        RequireComponent<Collider>(objectiveObject, "AIQuest_Objective");

        if (tracker.TargetObjective != objective)
        {
            throw new InvalidOperationException("Quest marker tracker must reference the objective.");
        }

        if (tracker.MarkerVisual != markerVisual.transform)
        {
            throw new InvalidOperationException("Quest marker tracker must reference the marker visual.");
        }

        tracker.RefreshMarker();
        if (!tracker.MarkerVisible || !markerVisual.activeSelf)
        {
            throw new InvalidOperationException("Quest marker should be visible before the target is reached.");
        }

        if (objective.Reached)
        {
            throw new InvalidOperationException("Objective should start unreached.");
        }

        var expectedDirection = objective.transform.position - player.transform.position;
        expectedDirection.y = 0f;
        expectedDirection.Normalize();
        if (Vector3.Dot(tracker.LastDirection, expectedDirection) < 0.99f)
        {
            throw new InvalidOperationException("Quest marker must point from the player toward the objective.");
        }

        player.transform.position = objective.transform.position + new Vector3(0.15f, 0f, 0.15f);
        tracker.RefreshMarker();

        if (!objective.Reached)
        {
            throw new InvalidOperationException("Objective should mark reached when the player arrives.");
        }

        if (tracker.MarkerVisible || markerVisual.activeSelf)
        {
            throw new InvalidOperationException("Quest marker should update and hide after the target is reached.");
        }

        Debug.Log("AIQuestMarkerSceneValidator passed.");
    }

    private static GameObject RequireObject(string objectName)
    {
        var found = GameObject.Find(objectName);
        if (found == null)
        {
            throw new InvalidOperationException($"Required scene object is missing: {objectName}");
        }

        return found;
    }

    private static T RequireComponent<T>(GameObject target, string objectName) where T : Component
    {
        var component = target.GetComponent<T>();
        if (component == null)
        {
            throw new InvalidOperationException($"{objectName} is missing required component {typeof(T).Name}.");
        }

        return component;
    }
}
