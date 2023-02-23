<script setup lang="ts">
import HelpMenu from './HelpMenu.vue'

</script>

<template>
    <HelpMenu>
        <h1 class="center">Color codes</h1>
        <table class="maxWidth dataTable">
            <thead>
                <tr>
                    <td>Color</td>
                    <td>Meaning</td>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td data-poll-status="active"></td>
                    <td>Service active</td>
                </tr>
                <tr>
                    <td data-poll-status="inactive"></td>
                    <td>Service inactive</td>
                </tr>
                <tr>
                    <td data-poll-status="active debug"></td>
                    <td>Service active (debug)</td>
                </tr>
                <tr>
                    <td data-poll-status="inactive debug"></td>
                    <td>Service inactive (debug)</td>
                </tr>
                <tr>
                    <td data-poll-status="error"></td>
                    <td>Service encountered error</td>
                </tr>
                <tr>
                    <td data-poll-status="polling"></td>
                    <td>Service polling data</td>
                </tr>
            </tbody>
        </table>
    </HelpMenu>
</template>
    