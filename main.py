# Author: Aidan Levy
# Creation Date: Jan 19, 2025
# Description: 
#
# Enter either a mp3 file name on your system
# or a youtube link and get an outputted
# bass-boosted version!
#
# README.txt exists for more help!

from pydub import AudioSegment
from scipy.signal import butter, sosfilt
import numpy as np
import os
import subprocess

def get_choice():
    choice = -1
    while choice < 1 or choice > 2:
        print("1. Enter YouTube link")
        print("2. Enter file name")
        choice = int(input(">> "))
    return choice

def bass_boost(infile, outfile, boost_db=10, cutoff=150):
    audio = AudioSegment.from_file(infile)
    audio = audio.set_channels(1)
    samples = np.array(audio.get_array_of_samples())
    samples = samples / (2 ** (audio.sample_width * 8 - 1))

    def low_shelf_filter(samples, boost_db, cutoff, fs):
        nyquist = 0.5 * fs
        norm_cutoff = cutoff / nyquist
        sos = butter(2, norm_cutoff, btype='low', output='sos')
        boosted_samples = sosfilt(sos, samples)
        gain = 10 ** (boost_db / 20)
        boosted_samples = samples + boosted_samples * gain
        return boosted_samples

    def high_shelf_filter(samples, boost_db, cutoff, fs):
        nyquist = 0.5 * fs
        norm_cutoff = cutoff / nyquist
        sos = butter(2, norm_cutoff, btype='high', output='sos')
        boosted_samples = sosfilt(sos, samples)
        gain = 10 ** (boost_db / 20)
        return samples + boosted_samples * gain

    fs = audio.frame_rate
    boosted_samples = low_shelf_filter(samples, boost_db, cutoff, fs)
    boosted_samples = high_shelf_filter(boosted_samples, boost_db=5, cutoff=3000, fs=fs)
    boosted_samples = boosted_samples / (np.max(np.abs(boosted_samples)) + 1e-10)
    boosted_samples = (boosted_samples * (2 ** (audio.sample_width * 8 - 1))).astype(np.int16)
    boosted_audio = audio._spawn(boosted_samples.tobytes())
    boosted_audio.export(outfile, format="wav")
    print(f"Bass boosted audio saved to: {outfile}")

def download(link, output_folder="input"):
    os.makedirs(output_folder, exist_ok=True)
    custom_name = input("Enter a custom name for the file (without extension): ").strip()
    sanitized_name = "".join(c for c in custom_name if c.isalnum() or c == " ").strip()
    output_file = os.path.join(output_folder, f"{sanitized_name}.mp3")
    command = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--no-playlist",
        "--no-cache-dir",
        "--force-overwrites",
        "-o", output_file,
        link
    ]
    subprocess.run(command, check=True)
    if not os.path.exists(output_file):
        raise FileNotFoundError(f"Download failed: {output_file} was not created.")
    return output_file


def main():
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    choice = get_choice()

    if choice == 1:
        link = input("Please enter a YouTube link: ")
        infile = download(link)
        outfile = os.path.join("output", "output_" + os.path.basename(infile))
    elif choice == 2:
        infile = input("Please enter an input file: ")
        infile = os.path.join("input", infile)
        if not os.path.exists(infile):
            print(f"File '{infile}' does not exist!")
            return
        outfile = os.path.join("output", "output_" + os.path.basename(infile))

    print(f"Processing file: {infile}")
    bass_boost(infile, outfile)

    print(f"Infile: {infile} | Outfile: {outfile}")

if __name__ == '__main__':
    main()
