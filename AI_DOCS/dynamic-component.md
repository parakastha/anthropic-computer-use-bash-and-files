# Vue.js Special Elements

## `<component>`

The `<component>` element is a "meta component" used for rendering dynamic components or elements. The actual component to render is determined by the `is` prop.

### Props

- `is` (`string` | `Component`): The component to render. When `is` is a string, it can be either an HTML tag name or a registered component name. Alternatively, `is` can be directly bound to a component definition.

### Examples

**Rendering components by registered name (Options API):**

```vue
<script>
import Foo from './Foo.vue'
import Bar from './Bar.vue'

export default {
  components: { Foo, Bar },
  data() {
    return {
      view: 'Foo'
    }
  }
}
</script>

<template>
  <component :is="view" />
</template>
```

**Rendering components by definition (Composition API with `<script setup>`):**

```vue
<script setup>
import Foo from './Foo.vue'
import Bar from './Bar.vue'
</script>

<template>
  <component :is="Math.random() > 0.5 ? Foo : Bar" />
</template>
```

**Rendering HTML elements:**

```html
<template>
  <component :is="href ? 'a' : 'span'"></component>
</template>
```

**Rendering built-in components:**

```vue
<script>
import { Transition, TransitionGroup } from 'vue'

export default {
  components: {
    Transition,
    TransitionGroup
  }
}
</script>

<template>
  <component :is="isGroup ? 'TransitionGroup' : 'Transition'">
    ...
  </component>
</template>
```

## `<slot>`

The `<slot>` element denotes slot content outlets in templates.

### Props

- `name` (`string`): Specifies the slot name. If not provided, it will render the default slot.
- Any additional attributes passed to the `<slot>` element will be passed as slot props to the scoped slot defined in the parent.

### Details

The `<slot>` element will be replaced by its matched slot content. The element itself is not rendered in the DOM.

## `<template>`

The `<template>` tag is used as a placeholder when we want to use a built-in directive without rendering an element in the DOM.

### Details

The special handling for `<template>` is only triggered if it is used with one of these directives:

- `v-if`, `v-else-if`, or `v-else`
- `v-for`
- `v-slot`

If none of those directives are present, it will be rendered as a native `<template>` element instead.

A `<template>` with `v-for` can also have a `key` attribute. All other attributes and directives will be discarded, as they aren't meaningful without a corresponding element.

Single-file components use a top-level `<template>` tag to wrap the entire template. That usage is separate from the use of `<template>` described above. That top-level tag is not part of the template itself and doesn't support template syntax, such as directives.