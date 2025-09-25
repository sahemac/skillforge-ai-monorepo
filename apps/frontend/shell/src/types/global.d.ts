/// <reference types="react" />
/// <reference types="react-dom" />
/// <reference types="react/jsx-runtime" />

declare module 'react' {
  const React: any;
  export = React;
}

declare module 'react/jsx-runtime' {
  export const jsx: any;
  export const jsxs: any;
  export const Fragment: any;
}

declare namespace JSX {
  interface Element extends React.ReactElement<any, any> {}
  interface IntrinsicElements {
    [elemName: string]: any;
  }
  interface ElementAttributesProperty {
    props: {};
  }
  interface ElementChildrenAttribute {
    children: {};
  }
}

declare module '*.svg' {
  const content: string;
  export default content;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.jpeg' {
  const content: string;
  export default content;
}

declare module '*.gif' {
  const content: string;
  export default content;
}

declare module '*.css' {
  const content: Record<string, string>;
  export default content;
}

declare module '*.scss' {
  const content: Record<string, string>;
  export default content;
}

declare module '*.module.css' {
  const content: Record<string, string>;
  export default content;
}

declare module '*.module.scss' {
  const content: Record<string, string>;
  export default content;
}

declare global {
  interface Window {
    __REDUX_DEVTOOLS_EXTENSION_COMPOSE__?: typeof import('redux').compose;
  }
}

export {};