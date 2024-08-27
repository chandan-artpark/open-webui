from fastapi import Depends, FastAPI, HTTPException, status, Request
from datetime import datetime, timedelta
from typing import List, Union, Optional

from fastapi import APIRouter
from pydantic import BaseModel
import json
import requests
import logging

from apps.webui.models.models import Models, ModelModel, ModelForm, ModelResponse

from utils.utils import get_verified_user, get_admin_user
from constants import ERROR_MESSAGES
from config import AGENT_API_BASE_URL

router = APIRouter()

###########################
# getModels
###########################


@router.get("/", response_model=List[ModelResponse])
async def get_models(user=Depends(get_verified_user)):
    return Models.get_all_models()


############################
# AddNewModel
############################


@router.post("/add", response_model=Optional[ModelModel])
async def add_new_model(
    request: Request,
    form_data: ModelForm,
    user=Depends(get_admin_user),
):
    if form_data.id in request.app.state.MODELS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.MODEL_ID_TAKEN,
        )
    else:
        model = Models.insert_new_model(form_data, user.id)

        if model:
            return model
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.DEFAULT(),
            )


############################
# GetModelById
############################


@router.get("/", response_model=Optional[ModelModel])
async def get_model_by_id(id: str, user=Depends(get_verified_user)):
    model = Models.get_model_by_id(id)

    if model:
        return model
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# UpdateModelById
############################


@router.post("/update", response_model=Optional[ModelModel])
async def update_model_by_id(
    request: Request,
    id: str,
    form_data: ModelForm,
    user=Depends(get_admin_user),
):
    model = Models.get_model_by_id(id)
    if model:
        model = Models.update_model_by_id(id, form_data)

        try:
            response = requests.post(f"{AGENT_API_BASE_URL}/models/update", json={
                "name": form_data.name,
                "data": form_data.meta.knowlwdge[-1],
                "status": "updated"
            })
            response.raise_for_status()
            logging.debug("Successfully sent to agent_router/messages")
        except Exception as e:
            logging.error(f"Error sending to agent_router/messages: {e}")

        return model
    else:
        if form_data.id in request.app.state.MODELS:
            model = Models.insert_new_model(form_data, user.id)
            if model:
                return model
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ERROR_MESSAGES.DEFAULT(),
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.DEFAULT(),
            )


############################
# DeleteModelById
############################


@router.delete("/delete", response_model=bool)
async def delete_model_by_id(id: str, user=Depends(get_admin_user)):
    result = Models.delete_model_by_id(id)
    return result
