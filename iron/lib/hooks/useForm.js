import useOnChange from "./useOnChange";
import { useState, useEffect } from "react";

function useForm({ service, initial }) {
  const { data, onChange } = useOnChange(initial || {});
  const [id, setId] = useState(0);
  const create = () => setId((prev) => prev + 1);
  useEffect(() => {
    if (id) {
      (async () => {
        const res = await fetch(`/rest/${service}`, {
          method: "POST",
          body: JSON.stringify(data),
          headers: {
            "content-type": "application/json",
          },
        });
      })();
    }
  }, [id]);
  return { create, onChange };
}

export default useForm;
