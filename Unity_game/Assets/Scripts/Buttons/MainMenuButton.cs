﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.SceneManagement;

public class MainMenuButton : MonoBehaviour, IPointerUpHandler
{
    public void OnPointerUp(PointerEventData eventData)
    {
        Time.timeScale = 1;
        SceneManager.LoadScene("Scenes/MainMenuScene", LoadSceneMode.Single);
    }
}