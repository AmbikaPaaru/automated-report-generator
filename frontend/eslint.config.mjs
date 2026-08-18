import nextConfig from "eslint-config-next";

// eslint-config-next's default export is already a native flat-config array
// (includes "next" + "next/typescript") -- no FlatCompat/legacy bridge needed.
const eslintConfig = [...nextConfig];

export default eslintConfig;
