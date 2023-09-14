<script setup lang="ts">
import brainImg from "@/assets/images/brain.png"

defineOptions({
    name: 'AppHeader'
})
</script>


<template>
    <header class="default-container h-[80px] flex items-center justify-start">
        <div class="flex items-center gap-4">
            <img :src="brainImg" alt="Brain icon">
            <p class="font-bold text-4xl" style="font-family: 'Advent Pro', sans-serif;">
                GreyMatter
            </p>
        </div>
    </header>
</template>