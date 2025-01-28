###################################### Imports #####################################################

import sys
import numpy as np
import torchaudio
from pydantic import BaseModel
from pathlib import Path
from fastapi import FastAPI, HTTPException
from openunmix import predict

################## Setting Up the Application and Save Directory ###################################

sys.path.append("../")
app = FastAPI()
save_path = Path("save/")
save_path.mkdir(parents=True, exist_ok=True)


################################# Data Model Definition ############################################
class AudioRequest(BaseModel):
    file_path: str


################################## separate_ummix Function #########################################
def separate_ummix(waveform, sample_rate):
    estimates = predict.separate(
        audio=waveform,
        rate=sample_rate,
        # model_str_or_path="unmix/unmix-vocal",
    )
    return estimates


############################### API Endpoint Definition ############################################
@app.post("/separate_sota")
async def separate_sota_by_path(audio_request: AudioRequest):
    audio_file_path = Path(audio_request.file_path)
    if not audio_file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    waveform, sample_rate = torchaudio.load(audio_file_path)
    separated_audio = separate_ummix(waveform, sample_rate)

    result = {"sr": sample_rate}
    for stem in ["vocals", "drums", "bass", "other"]:
        stem_waveform = separated_audio[stem]
        file_path = save_path / f"{stem}.npy"
        np.save(file_path, stem_waveform)

        # Return the full absolute path for the files
        result[stem] = str(file_path.resolve())  # Full path returned to Streamlit

    return result
