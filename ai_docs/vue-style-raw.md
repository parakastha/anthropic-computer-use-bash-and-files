# ai_docs/vue-style-raw.md

```html
<template>
  <div :class="$style.container">
    <!-- class binding -->
    <div :class="{ [$style.active]: isActive }">Active</div>
    <div :class="[$style.static, isActive ? $style.active : '']">
      Static and Active
    </div>

    <!-- style binding -->
    <div :style="{ color: activeColor, fontSize: fontSize + 'px' }">
      Style Binding
    </div>
    <div :style="[baseStyles, overridingStyles]">Combining Styles</div>
  </div>
</template>

<script>
import styles from './component.module.css'

export default {
  data() {
    return {
      isActive: true,
      activeColor: 'green',
      fontSize: 16,
      baseStyles: {
        backgroundColor: '#000',
        color: '#fff'
      },
      overridingStyles: {
        color: '#8b0000',
        fontSize: '20px'
      }
    }
  }
}
</script>

<style module>
.container {
  padding: 20px;
}
.active {
  font-weight: bold;
}
.static {
  font-style: italic;
}
</style>
```