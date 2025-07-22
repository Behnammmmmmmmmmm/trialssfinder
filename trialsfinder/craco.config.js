module.exports = {
  eslint: {
    enable: true,
    mode: "extends",
    configure: {
      rules: {
        "import/no-unresolved": "off",
        "import/no-cycle": "off",
        "import/namespace": "off",
        "import/order": "off",
        "import/default": "off"
      },
      settings: {
        "import/resolver": {
          node: {
            extensions: [".js", ".jsx", ".ts", ".tsx"],
            moduleDirectory: ["node_modules", "src/"]
          }
        }
      }
    }
  }
};