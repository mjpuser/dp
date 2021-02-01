import useOnChange from "./useOnChange";
import { useEffect } from "react";
import Pipeline from "../types/resource/pipeline";
import Vertex from "../types/resource/vertex";
import useIncrement from "./useIncrement";
import { Resource } from "../types/resource";

type UseFormOptions<T extends Resource> = {
  service:
    T extends Vertex ? 'vertex' :
    T extends Pipeline ? 'pipeline' :
    'error',
  initial?: Partial<T>
}

function useForm<T extends Resource>({ initial, service }: UseFormOptions<T>) {
  const { data, onChange } = useOnChange<T>(initial);
  const { count, increment } = useIncrement();
  useEffect(() => {
    if (count) {
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
  }, [count]);
  return { create: increment, onChange };
}

export default useForm;
