import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  {
    rules: {
      // The mounted-hydration pattern (single setState in empty-dep useEffect) is
      // standard React practice for client-only state. Overly strict — disable.
      "react-hooks/set-state-in-effect": "off",
    },
  },
]);

export default eslintConfig;
