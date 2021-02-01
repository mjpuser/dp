import { Button, FormControl, Input, InputLabel } from "@material-ui/core";
import useForm from "../../lib/hooks/useForm";
import Vertex from "../../lib/types/resource/vertex";
import FormSelect from "../../components/form/select";

export default function NewVertex({ pipelines, vertices, funcs }) {
  const { create, onChange } = useForm<Vertex>({ service: "vertex" });
  console.log(pipelines, vertices, funcs)
  return (
    <form noValidate autoComplete="off">
      <FormControl fullWidth>
        <InputLabel htmlFor="vertex-name">Name</InputLabel>
        <Input id="vertex-name" onChange={onChange("name")} />
      </FormControl>
      <FormSelect
        data={pipelines.map(p => ({ value: p.id, text: p.name}))}
        name="pipeline"
        onChange={onChange("pipeline_id")}
        label="Pipeline"
      />
      <FormControl fullWidth>
        <InputLabel htmlFor="vertex-routing-in">Input Routing Key</InputLabel>
        <Input id="vertex-routing-in" onChange={onChange("routing_key_in")} />
      </FormControl>
      <FormSelect
        data={funcs.map(({ name }) => ({ value: name, text: name }))}
        name="func"
        onChange={onChange("func")}
        label="Function"
      />
      <FormControl fullWidth>
        <InputLabel htmlFor="vertex-func-config">Function Config</InputLabel>
        <Input id="vertex-func-config" onChange={onChange("func_config")} />
      </FormControl>
      <Button variant="contained" color="primary" onClick={create}>
        Create
      </Button>
    </form>
  );
}

export async function getServerSideProps() {
  const types = ["pipeline", "func", "vertex"];
  const [pipelines, funcs, vertices] = await Promise.all(
    types.map(async (t) => {
      const res = await fetch(`http://rest:3000/${t}`);
      return await res.json();
    })
  );
  console.log(pipelines, vertices, funcs)

  return {
    props: {
      pipelines,
      funcs,
      vertices,
    },
  };
}
