<script setup lang="ts">
import { ref } from 'vue';
import AppHeader from './components/AppHeader.vue';
import type { PredictionResult } from "./types"

const imageInput = ref<HTMLInputElement | null>(null);


const loadedImageDataURL = ref<string | null>(null);
const loadedImage = ref<File | null>(null)


async function showImageAndGetPrediction(file: File | undefined) {
  if (file) {
    loadedImage.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      loadedImageDataURL.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
    await getPrediction();
  } else {
    loadedImage.value = null;
    loadedImageDataURL.value = null;
  }
}

async function loadImage() {
  console.log("File called")
  const file = imageInput.value?.files?.[0];
  await showImageAndGetPrediction(file);
}

async function handleDrop(e: DragEvent) {
  e.preventDefault();
  const file = e.dataTransfer?.files?.[0];
  await showImageAndGetPrediction(file);
}



const isPredictionLoading = ref(false);
const prediction = ref<PredictionResult | null>(null);


function getHumanReadableType(tumor_type: keyof PredictionResult['probabilities']) {
  switch (tumor_type) {
    case 'glioma':
      return 'Glioma'
    case 'meningioma':
      return 'Meningioma'
    case 'notumor':
      return 'No tumor'
    case 'pituitary':
      return 'Pituitary tumor'

    default:
      return ''
  }
}

function getHumanReadableResult(tumor_type: keyof PredictionResult['probabilities']) {
  switch (tumor_type) {
    case 'glioma':
      return 'According to the MRI, this tumor is most likely a <strong class="font-bold">Glioma</strong>'
    case 'meningioma':
      return 'According to the MRI, this tumor is most likely a <strong class="font-bold">Meningioma</strong>'
    case 'notumor':
      return 'According to the MRI, this patient most likely does not have a tumor'
    case 'pituitary':
      return 'According to the MRI, this tumor is most likely a <strong class="font-bold">pituitary tumor</strong>'

    default:
      return ''
  }
}


function getOrderedProbabilities(predictions: PredictionResult['probabilities']) {
  const orderedProbabilities = Object.entries(predictions).sort((a, b) => b[1] - a[1])
  return orderedProbabilities
}

async function getPrediction() {

  if (!loadedImage.value) {
    alert("Please upload an image")
  }

  isPredictionLoading.value = true;
  prediction.value = null;
  try {

    const formData = new FormData();
    formData.append('file', loadedImage.value as File);

    const response = await fetch('http://localhost:8000/predictions-for-uploaded-image', {
      method: 'POST',
      body: formData,
    });

    if (response.status === 200) {
      const data = await response.json() as PredictionResult;
      console.log(data.probabilities)
      isPredictionLoading.value = false;
      prediction.value = data
    }
  } catch (e) {
    console.log(e)
  } finally {
    isPredictionLoading.value = false;
  }
}

function clearPrediction() {
  prediction.value = null;
  loadedImageDataURL.value = null;
}
</script>

<template>
  <Teleport to="body">
    <AppHeader />
    <main class="h-[calc(100vh-80px)] flex flex-col lg:flex-row">
      <section class="w-full lg:w-1/2 flex items-center justify-center">
        <div @click="imageInput?.click()" @drop="handleDrop" @dragover.prevent
          class="w-[90%] aspect-square max-w-[550px] grid place-items-center rounded-xl cursor-pointer" :style="{
            backgroundImage: loadedImageDataURL ? `url(${loadedImageDataURL})` : 'linear-gradient(rgba(0,0,0,0.05), rgba(0,0,0,0.05))',
            backgroundSize: loadedImageDataURL ? 'cover' : 'auto',
            backgroundPosition: loadedImageDataURL ? 'center' : 'auto',
          }">
          <svg xmlns="http://www.w3.org/2000/svg" width="72" height="72" viewBox="0 0 24 24">
            <path :fill="loadedImageDataURL ? `#fff` :`rgba(0,0,0,0.9)`"
              d="M12 18q2.075 0 3.538-1.462Q17 15.075 17 13q0-2.075-1.462-3.538Q14.075 8 12 8Q9.925 8 8.463 9.462Q7 10.925 7 13q0 2.075 1.463 3.538Q9.925 18 12 18Zm0-2q-1.25 0-2.125-.875T9 13q0-1.25.875-2.125T12 10q1.25 0 2.125.875T15 13q0 1.25-.875 2.125T12 16Zm6-6q.425 0 .712-.288Q19 9.425 19 9t-.288-.713Q18.425 8 18 8t-.712.287Q17 8.575 17 9t.288.712Q17.575 10 18 10ZM4 21q-.825 0-1.412-.587Q2 19.825 2 19V7q0-.825.588-1.412Q3.175 5 4 5h3.15L8.7 3.325q.15-.15.337-.238Q9.225 3 9.425 3h5.15q.2 0 .388.087q.187.088.337.238L16.85 5H20q.825 0 1.413.588Q22 6.175 22 7v12q0 .825-.587 1.413Q20.825 21 20 21Zm16-2V7h-4.05l-1.825-2h-4.25L8.05 7H4v12Zm-8-6Z" />
          </svg>
          <input type="file" accept="image/*" class="hidden" ref="imageInput" @change="loadImage">
        </div>
      </section>
      <section class="w-full lg:w-1/2 flex items-center justify-center">
        <div v-if="!isPredictionLoading && !prediction">
          <p class="mx-auto w-[80%] text-center text-4xl text-[rgba(0,0,0,0.3)]">Upload a photo of a MRI scan to analyze
            the possibility of a tumor</p>
        </div>
        <div v-else-if="isPredictionLoading" class="flex flex-col gap-4 items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24">
            <rect width="7.33" height="7.33" x="1" y="1" fill="currentColor">
              <animate id="svgSpinnersBlocksWave0" attributeName="x" begin="0;svgSpinnersBlocksWave1.end+0.2s" dur="0.6s"
                values="1;4;1" />
              <animate attributeName="y" begin="0;svgSpinnersBlocksWave1.end+0.2s" dur="0.6s" values="1;4;1" />
              <animate attributeName="width" begin="0;svgSpinnersBlocksWave1.end+0.2s" dur="0.6s"
                values="7.33;1.33;7.33" />
              <animate attributeName="height" begin="0;svgSpinnersBlocksWave1.end+0.2s" dur="0.6s"
                values="7.33;1.33;7.33" />
            </rect>
            <rect width="7.33" height="7.33" x="8.33" y="1" fill="currentColor">
              <animate attributeName="x" begin="svgSpinnersBlocksWave0.begin+0.1s" dur="0.6s" values="8.33;11.33;8.33" />
              <animate attributeName="y" begin="svgSpinnersBlocksWave0.begin+0.1s" dur="0.6s" values="1;4;1" />
              <animate attributeName="width" begin="svgSpinnersBlocksWave0.begin+0.1s" dur="0.6s"
                values="7.33;1.33;7.33" />
              <animate attributeName="height" begin="svgSpinnersBlocksWave0.begin+0.1s" dur="0.6s"
                values="7.33;1.33;7.33" />
            </rect>
            <rect width="7.33" height="7.33" x="1" y="8.33" fill="currentColor">
              <animate attributeName="x" begin="svgSpinnersBlocksWave0.begin+0.1s" dur="0.6s" values="1;4;1" />
              <animate attributeName="y" begin="svgSpinnersBlocksWave0.begin+0.1s" dur="0.6s" values="8.33;11.33;8.33" />
              <animate attributeName="width" begin="svgSpinnersBlocksWave0.begin+0.1s" dur="0.6s"
                values="7.33;1.33;7.33" />
              <animate attributeName="height" begin="svgSpinnersBlocksWave0.begin+0.1s" dur="0.6s"
                values="7.33;1.33;7.33" />
            </rect>
            <rect width="7.33" height="7.33" x="15.66" y="1" fill="currentColor">
              <animate attributeName="x" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s"
                values="15.66;18.66;15.66" />
              <animate attributeName="y" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s" values="1;4;1" />
              <animate attributeName="width" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s"
                values="7.33;1.33;7.33" />
              <animate attributeName="height" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s"
                values="7.33;1.33;7.33" />
            </rect>
            <rect width="7.33" height="7.33" x="8.33" y="8.33" fill="currentColor">
              <animate attributeName="x" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s" values="8.33;11.33;8.33" />
              <animate attributeName="y" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s" values="8.33;11.33;8.33" />
              <animate attributeName="width" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s"
                values="7.33;1.33;7.33" />
              <animate attributeName="height" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s"
                values="7.33;1.33;7.33" />
            </rect>
            <rect width="7.33" height="7.33" x="1" y="15.66" fill="currentColor">
              <animate attributeName="x" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s" values="1;4;1" />
              <animate attributeName="y" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s"
                values="15.66;18.66;15.66" />
              <animate attributeName="width" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s"
                values="7.33;1.33;7.33" />
              <animate attributeName="height" begin="svgSpinnersBlocksWave0.begin+0.2s" dur="0.6s"
                values="7.33;1.33;7.33" />
            </rect>
            <rect width="7.33" height="7.33" x="15.66" y="8.33" fill="currentColor">
              <animate attributeName="x" begin="svgSpinnersBlocksWave0.begin+0.3s" dur="0.6s"
                values="15.66;18.66;15.66" />
              <animate attributeName="y" begin="svgSpinnersBlocksWave0.begin+0.3s" dur="0.6s" values="8.33;11.33;8.33" />
              <animate attributeName="width" begin="svgSpinnersBlocksWave0.begin+0.3s" dur="0.6s"
                values="7.33;1.33;7.33" />
              <animate attributeName="height" begin="svgSpinnersBlocksWave0.begin+0.3s" dur="0.6s"
                values="7.33;1.33;7.33" />
            </rect>
            <rect width="7.33" height="7.33" x="8.33" y="15.66" fill="currentColor">
              <animate attributeName="x" begin="svgSpinnersBlocksWave0.begin+0.3s" dur="0.6s" values="8.33;11.33;8.33" />
              <animate attributeName="y" begin="svgSpinnersBlocksWave0.begin+0.3s" dur="0.6s"
                values="15.66;18.66;15.66" />
              <animate attributeName="width" begin="svgSpinnersBlocksWave0.begin+0.3s" dur="0.6s"
                values="7.33;1.33;7.33" />
              <animate attributeName="height" begin="svgSpinnersBlocksWave0.begin+0.3s" dur="0.6s"
                values="7.33;1.33;7.33" />
            </rect>
            <rect width="7.33" height="7.33" x="15.66" y="15.66" fill="currentColor">
              <animate id="svgSpinnersBlocksWave1" attributeName="x" begin="svgSpinnersBlocksWave0.begin+0.4s" dur="0.6s"
                values="15.66;18.66;15.66" />
              <animate attributeName="y" begin="svgSpinnersBlocksWave0.begin+0.4s" dur="0.6s"
                values="15.66;18.66;15.66" />
              <animate attributeName="width" begin="svgSpinnersBlocksWave0.begin+0.4s" dur="0.6s"
                values="7.33;1.33;7.33" />
              <animate attributeName="height" begin="svgSpinnersBlocksWave0.begin+0.4s" dur="0.6s"
                values="7.33;1.33;7.33" />
            </rect>
          </svg>
          <p class="text-xl">Analyzing</p>
        </div>
        <div v-else-if="!isPredictionLoading && prediction" class="flex flex-col items-center justify-center gap-8">
          <p class="mx-auto w-[80%] text-center text-4xl text-[rgba(0,0,0,0.8)]" v-html="getHumanReadableResult(prediction.type)" />
          <h2 class="text-left w-4/5 text-2xl font-bold">Calculated probabilities</h2>
          <ul class="flex flex-col gap-2 w-4/5">
            <li v-for="([tumor_type, probability], index) in getOrderedProbabilities(prediction.probabilities)"
              :key="index" class="flex items-center justify-between w-[100%] mx-auto">
              <p class="text-xl font-semibold">{{ getHumanReadableType(tumor_type as keyof PredictionResult['probabilities']) }}</p>
              <p class="text-xl">{{ probability.toFixed(15) }}%</p>
            </li>
          </ul>
          <button class="mx-auto py-2 px-4 rounded-md bg-blue-500 text-white text-md hover:-translate-y-[2px] active:-translate-y-[1px] transition-all " @click="clearPrediction">Clear
            results</button>
        </div>
      </section>
    </main>
  </Teleport>
</template>