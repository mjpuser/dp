export const service = function (name) {
  let domain = "http://localhost:3000";
  switch (name) {
    case "rest":
      return `${domain}/rest`;
  }
};
