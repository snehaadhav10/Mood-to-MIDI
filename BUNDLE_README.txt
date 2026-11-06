# P47 Mood-to-MIDI + MuseGAN bundle

This bundle contains:
- The existing P47_Mood_to_MIDI application copied from the local Downloads folder.
- The MuseGAN source repository.
- The locally available pretrained checkpoint files under musegan-main/exp/default/model.

## Important compatibility note

The included MuseGAN repository pins very old dependencies, including tensorflow-gpu==1.10.1,
NumPy 1.14.5 and SciPy 1.1.0. The original inference script uses TensorFlow 1.x APIs
(tf.placeholder, tf.Session). Do not install its requirements into your existing Python 3.11
environment, and do not assume the model runs on native Windows without compatibility work.

The checkpoint is bundled, but this package does not claim that MuseGAN has been successfully
loaded or connected to the application. The original model inference must be tested in a
compatible environment and the app's generator integration must be verified.

## Local paths used to create this bundle

Mood-to-MIDI source: C:\Users\Dell\Downloads\P47_Mood_to_MIDI
MuseGAN source: C:\Users\Dell\Downloads\musegan-main\musegan-main

## Next step

Open the project folder and inspect its README and requirements. Keep your original folders;
this ZIP is a copy.
