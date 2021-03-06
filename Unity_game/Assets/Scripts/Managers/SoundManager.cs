﻿using System.Collections.Generic;
using UnityEngine;

public class SoundManager : MonoBehaviour
{
    private Dictionary<int, AudioSource> _audioSources;
    private List<int> _audioSourcesToDelete;
    [SerializeField] private AudioSource _buttonSound;
    [SerializeField] private AudioSource _baseExplosionSound;
    [SerializeField] private AudioSource _baseDamageSound;
    [SerializeField] private AudioSource _victorySound;

    // Start is called before the first frame update
    private void Start()
    {
        _audioSources = new Dictionary<int, AudioSource>();
        _audioSourcesToDelete = new List<int>();
    }

    // Update is called once per frame
    private void Update()
    {
        for (int i = 0; i < _audioSourcesToDelete.Count; i++)
        {
            int instanceId = _audioSourcesToDelete[i];
            if (!_audioSources[instanceId].isPlaying)
            {
                Destroy(_audioSources[instanceId]);
                _audioSources.Remove(instanceId);
                _audioSourcesToDelete[i] = 0;
            }
        }

        _audioSourcesToDelete = _audioSourcesToDelete.FindAll(e => e != 0);
    }

    public void AddAudioSource(int instanceId, AudioClip clip)
    {
        AudioSource audioSource = gameObject.AddComponent<AudioSource>();
        audioSource.clip = clip;
        _audioSources.Add(instanceId, audioSource);
    }

    public void PlaySound(int instanceId)
    {
        _audioSources[instanceId].Play();
    }

    public void PlayButtonSound()
    {
        _buttonSound.Play();
    }

    public void PlayBaseExplosionSound()
    {
        _baseExplosionSound.Play();
    }

    public void PlayBaseDamageSound()
    {
        _baseDamageSound.Play();
    }

    public void PlayVictorySound()
    {
        _victorySound.Play();
    }

    public void RemoveAudioSource(int instanceId)
    {
        _audioSourcesToDelete.Add(instanceId);
    }
}